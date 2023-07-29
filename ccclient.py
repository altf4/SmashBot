#!/usr/bin/python3
import time
import traceback
import uuid
from typing import Optional, Tuple

import jwt
import json
import asyncio
import aiohttp
import websockets
import os
import concurrent.futures

from crowdcontrol_listener import ITEMS, ccSocket, getItemInt, trySpawnItemInt

WSS_ENDPOINT_SUBDOMAIN = "r8073rtqd8"
WEBSOCKET_URL = f"wss://{WSS_ENDPOINT_SUBDOMAIN}.execute-api.us-east-1.amazonaws.com/staging"

HTTP_ENDPOINT_SUBDOMAIN = "9n5yuz1umd"
HTTP_ROOT_URL = f"{HTTP_ENDPOINT_SUBDOMAIN}.execute-api.us-east-1.amazonaws.com"
START_SESSION_ENDPOINT = f"https://{HTTP_ROOT_URL}/gameSession.startSession"
END_SESSION_ENDPOINT = f"https://{HTTP_ROOT_URL}/gameSession.stopSession"

START_SESSION_BODY = {"gamePackID": "SuperSmashBrosMeleeESA", "effectReportArgs": []}

TIMEOUT = 3.0
MAX_WAIT = 60.0
SPAWNS_OFF = False


def send_and_read(item: int) -> bool:
    global SPAWNS_OFF
    if not SPAWNS_OFF:
        trySpawnItemInt(item)
    time.sleep(0.017 * 4)
    success = False
    try:
        while True:
            datagram = os.read(ccSocket, 1)
            if datagram == b"\xFF":
                SPAWNS_OFF = True
            elif datagram == b"\xFE":
                SPAWNS_OFF = False
            elif datagram[0] == item:
                success = True
    except BlockingIOError:
        pass
    return success


class CrowdControl:
    session_id: Optional[str] = None
    user: Optional[dict] = None
    auth_token: Optional[str] = None

    def __init__(self):
        self.ws = None
        if os.path.exists("cc_auth_token.txt"):
            with open("cc_auth_token.txt", "r") as file:
                self.auth_token = file.read().strip()
                self.load_user()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.lock = asyncio.Lock()
        self.item_task: Optional[asyncio.Task] = None

    def load_user(self):
        if not self.auth_token:
            return
        self.user = jwt.decode(self.auth_token, options={"verify_signature": False})

    async def call_endpoint(self, session: aiohttp.ClientSession, url: str, data_raw: dict) -> Tuple[int, dict]:
        try:
            headers = {"Authorization": "cc-auth-token " + self.auth_token}
            data = json.dumps(data_raw)
            async with session.post(url, headers=headers, data=data) as response:
                return response.status, await response.json()
        except Exception as error:
            traceback.print_exc()
            return 500, {"error": str(error)}

    async def send_status(self, effect: str, effect_id: str, websocket: websockets.WebSocketClientProtocol, status: str):
        print(f"Handling {effect} produced status {status}")
        rand_id: str = str(uuid.uuid4())
        response_data = {
            "token": self.auth_token,
            "call": {
                "method": "effectResponse",
                "args": [
                    {
                        "request": effect_id,
                        "id": rand_id,
                        "stamp": int(time.time()),
                        "status": status,
                        "message": "",
                    },
                ],
                "id": rand_id,
                "type": "call"
            }
        }
        response_body = {"action": "rpc", "data": json.dumps(response_data)}
        await websocket.send(json.dumps(response_body))

    async def spawn_item(self, item: int, effect: str, effect_id: str, websocket: websockets.WebSocketClientProtocol):
        result: Optional[bool] = None
        while True:
            # Keep trying to spawn the item until we get the signal that it spawned
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(self.executor, send_and_read, item, result)
            if result:
                await self.send_status(effect, effect_id, websocket, 'success')
                return

    async def delay_effect(self, started: float, effect: str, effect_id: str, websocket: websockets.WebSocketClientProtocol):
        if (time.time() - started) > 60:
            await self.send_status(effect, effect_id, websocket, 'failTemporary')
        else:
            await self.send_status(effect, effect_id, websocket, 'delayEstimated')
            await asyncio.sleep(5)
            asyncio.create_task(self.handle_effect(started, effect, effect_id, websocket))

    async def handle_effect(self, started: float, effect: str, effect_id: str, websocket: websockets.WebSocketClientProtocol):
        try:
            effect_parts = effect.split('_', 1)
            if effect_parts[0] == "spawnitem":
                if effect_parts[1] not in ITEMS:
                    await self.send_status(effect, effect_id, websocket, 'failPermanent')
                    return
                async with self.lock:
                    if (time.time() - started) > MAX_WAIT:
                        await self.send_status(effect, effect_id, websocket, 'failTemporary')
                        return
                    future = self.spawn_item(getItemInt(effect_parts[1]), effect, effect_id, websocket)
                    try:
                        await asyncio.create_task(asyncio.wait_for(future, TIMEOUT))
                    except asyncio.TimeoutError:
                        await self.delay_effect(started, effect, effect_id, websocket)
            else:
                print("Unknown code:", effect_parts[0])
                await self.send_status(effect, effect_id, websocket, 'failPermanent')
        except Exception:
            print("Error handling effect")
            traceback.print_exc()
            await self.send_status(effect, effect_id, websocket, 'failTemporary')

    async def listen_to_websocket(self, session: aiohttp.ClientSession):
        async with websockets.connect(WEBSOCKET_URL, extra_headers={"User-Agent": "SmashBot CrowdControl"}) as websocket:
            self.ws = websocket
            # Fetch user token if not set
            if not self.auth_token:
                await websocket.send(json.dumps({"action": "whoami"}))
                while True:
                    whoami_raw: str = await websocket.recv()
                    whoami: dict = json.loads(whoami_raw)
                    if whoami.get('type') == 'whoami':
                        connection_id = whoami['payload']['connectionID']
                        auth_url = f"https://beta-auth.crowdcontrol.live/?connectionID={connection_id}"
                        print(f"Please visit {auth_url} to sign in and authorize this app")
                    elif whoami.get('type') == 'login-success':
                        self.auth_token = whoami['payload']['token']
                        with open("cc_auth_token.txt", "w") as file:
                            file.write(self.auth_token)
                        self.load_user()
                        print(f"Successfully logged in")
                        break
            # Subscribe to packets for user
            print("Subscribing to packets...")
            subscribe_data = {"topics": [f"pub/{self.user['ccUID']}"]}
            subscribe_body = {"action": "subscribe", "data": json.dumps(subscribe_data)}
            await websocket.send(json.dumps(subscribe_body))
            # Start session
            print("Starting session...")
            s_status, s_data = await self.call_endpoint(session, START_SESSION_ENDPOINT, START_SESSION_BODY)
            self.session_id: Optional[str] = s_data.get('result', {}).get('data', {}).get('gameSessionID', None)
            if 'error' in s_data:
                print(f"Error starting session: {s_data['error']}")
                return
            if not self.session_id:
                print(f"Error starting session: no session ID returned ({s_data})")
                return
            ext_url = f"https://beta-extension.crowdcontrol.live/#/{self.user['profileType']}/{self.user['originID']}"
            print(f"Session started; effects can now be purchased at {ext_url}")
            # Begin listening for packets
            print("Listening for packets...")
            while True:
                effect_purchase_raw: str = await websocket.recv()
                effect_purchase: dict = json.loads(effect_purchase_raw)
                if effect_purchase.get('type') == 'bad-request':
                    print(effect_purchase)
                elif effect_purchase.get('domain') != 'pub' or effect_purchase.get('type') != 'effect-request':
                    continue
                payload: dict = effect_purchase['payload']
                effect: dict = payload['effect']
                asyncio.create_task(self.handle_effect(time.time(), effect['effectID'], payload['requestID'], websocket))

    async def main(self):
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                await self.listen_to_websocket(session)
            except BaseException:
                traceback.print_exc()
            finally:
                if self.session_id:
                    out = {"gameSessionID": self.session_id}
                    code, data = await self.call_endpoint(session, END_SESSION_ENDPOINT, out)
                    print(f"Closing session {self.session_id} produced {code} {data}")
                print("Exiting")


if __name__ == '__main__':
    asyncio.run(CrowdControl().main())

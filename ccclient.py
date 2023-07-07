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

from spawnitem import send_item

WSS_ENDPOINT_SUBDOMAIN = "r8073rtqd8"
WEBSOCKET_URL = f"wss://{WSS_ENDPOINT_SUBDOMAIN}.execute-api.us-east-1.amazonaws.com/staging"

HTTP_ENDPOINT_SUBDOMAIN = "9n5yuz1umd"
HTTP_ROOT_URL = f"{HTTP_ENDPOINT_SUBDOMAIN}.execute-api.us-east-1.amazonaws.com"
START_SESSION_ENDPOINT = f"https://{HTTP_ROOT_URL}/gameSession.startSession"
END_SESSION_ENDPOINT = f"https://{HTTP_ROOT_URL}/gameSession.stopSession"

START_SESSION_BODY = {"gamePackID": "SuperSmashBrosMeleeESA", "effectReportArgs": []}


class CrowdControl:
    session_id: Optional[str] = None
    user: Optional[dict] = None
    auth_token: Optional[str] = os.getenv("CC_AUTH_TOKEN")

    def __init__(self):
        self.load_user()

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

    def handle_effect(self, effect: str) -> str:
        try:
            effect_parts = effect.split('_', 1)
            if effect_parts[0] == "spawnitem":
                return send_item(effect_parts[1])
            else:
                print("Unknown code:", effect_parts[0])
                return 'failPermanent'
        except Exception:
            print("Error handling effect")
            traceback.print_exc()
            return 'failTemporary'

    async def listen_to_websocket(self, session: aiohttp.ClientSession):
        async with websockets.connect(WEBSOCKET_URL) as websocket:
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
                if effect_purchase.get('domain') != 'pub' or effect_purchase.get('type') != 'effect-request':
                    continue
                payload: dict = effect_purchase['payload']
                effect: dict = payload['effect']
                status: str = self.handle_effect(effect['effectID'])
                print(f"Handling {effect['effectID']} produced status {status}")
                rand_id: str = str(uuid.uuid4())
                response_data = {
                    "token": self.auth_token,
                    "call": {
                        "method": "effectResponse",
                        "args": [
                            {
                                "request": payload['requestID'],
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

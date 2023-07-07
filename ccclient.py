import time
import traceback
import uuid
from typing import Optional

from cctypes import *
import json
import asyncio
import aiohttp
import websockets
import os

from spawnitem import send_item

# required environment variables (captured from app's dev tools):
#  CC_USER_ID: the Crowd Control user's ID
#  CC_AUTH_TOKEN: the Crowd Control user's auth token

WSS_ENDPOINT_SUBDOMAIN = "r8073rtqd8"
WEBSOCKET_URL = f"wss://{WSS_ENDPOINT_SUBDOMAIN}.execute-api.us-east-1.amazonaws.com/staging"

HTTP_ENDPOINT_SUBDOMAIN = "9n5yuz1umd"
HTTP_ROOT_URL = f"{HTTP_ENDPOINT_SUBDOMAIN}.execute-api.us-east-1.amazonaws.com"
START_SESSION_ENDPOINT = f"https://{HTTP_ROOT_URL}/gameSession.startSession"
END_SESSION_ENDPOINT = f"https://{HTTP_ROOT_URL}/gameSession.stopSession"


START_SESSION_BODY = {"gamePackID": "SuperSmashBrosMeleeESA", "effectReportArgs": []}


async def call_endpoint(session: aiohttp.ClientSession, url: str, data_raw: dict) -> tuple[int, dict]:
    try:
        headers = {"Authorization": "cc-auth-token " + os.environ["CC_AUTH_TOKEN"]}
        data = json.dumps(data_raw)
        async with session.post(url, headers=headers, data=data) as response:
            return response.status, await response.json()
    except Exception as error:
        return 500, {"error": str(error)}


def handle_effect(effect: str) -> EffectStatus:
    try:
        effect_parts = effect.split('_', 1)
        match effect_parts[0]:
            case 'spawnitem':
                return send_item(effect_parts[1])
            case _:
                print("Unknown code:", effect_parts[0])
                return 'failPermanent'
    except Exception:
        print("Error handling effect")
        traceback.print_exc()
        return 'failTemporary'


async def listen_to_websocket():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        # Subscribe to packets for user
        print("Subscribing to packets...")
        subscribe_data = {"topics": [f"pub/ccuid-{os.environ['CC_USER_ID']}"]}
        subscribe_body = {"action": "subscribe", "data": json.dumps(subscribe_data)}
        await websocket.send(json.dumps(subscribe_body))
        # Begin listening for packets
        print("Listening for packets...")
        while True:
            effect_purchase_raw: str = await websocket.recv()
            effect_purchase: PacketBody = json.loads(effect_purchase_raw)
            if effect_purchase.get('domain') != 'pub' or effect_purchase.get('type') != 'effect-request':
                continue
            payload: PacketPayload = effect_purchase['payload']
            effect: Effect = payload['effect']
            status: EffectStatus = handle_effect(effect['effectID'])
            print(f"Handling {effect['effectID']} produced status {status}")
            rand_id: str = str(uuid.uuid4())
            response_data = {
                "token": os.environ["CC_AUTH_TOKEN"],
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


async def main():
    if 'CC_AUTH_TOKEN' not in os.environ or 'CC_USER_ID' not in os.environ:
        print("Please set CC_AUTH_TOKEN and CC_USER_ID environment variables")
        return

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        s_status, s_data = await call_endpoint(session, START_SESSION_ENDPOINT, START_SESSION_BODY)
        if 'error' in s_data:
            print(f"Error starting session: {s_data['error']}")
            return
        session_id: Optional[str] = s_data.get('result', {}).get('data', {}).get('gameSessionID', None)
        if not session_id:
            print(f"Error starting session: no session ID returned ({s_data})")
            return
        print("Started session")
        try:
            await listen_to_websocket()
        except BaseException:
            traceback.print_exc()
            print("Closing session and exiting")
            await call_endpoint(session, END_SESSION_ENDPOINT, {"gameSessionID": session_id})

if __name__ == '__main__':
    asyncio.run(main())

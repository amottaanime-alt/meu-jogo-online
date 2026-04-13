import os

PORT = int(os.environ.get("PORT", 8765))

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print(f"Servidor rodando na porta {PORT}")
        await asyncio.Future()

import asyncio
import websockets
import json
import uuid




players = {}
connected = set()

async def handler(websocket):
    player_id = str(uuid.uuid4())
    players[player_id] = {"x": 100, "y": 100}
    connected.add(websocket)

    try:
        await websocket.send(json.dumps({
            "type": "init",
            "id": player_id
        }))

        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "move":
                players[player_id]["x"] = data["x"]
                players[player_id]["y"] = data["y"]

            state = json.dumps({
                "type": "state",
                "players": players
            })

            await asyncio.gather(*[
                ws.send(state) for ws in connected
            ])

    except:
        pass
    finally:
        connected.remove(websocket)
        del players[player_id]

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Servidor rodando em ws://localhost:8765")
        await asyncio.Future()  # roda pra sempre

if __name__ == "__main__":
    asyncio.run(main())
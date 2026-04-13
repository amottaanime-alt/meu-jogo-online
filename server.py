import asyncio
import websockets
import json
import uuid
import os

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

    except:
        pass
    finally:
        connected.remove(websocket)
        if player_id in players:
            del players[player_id]

# 🔁 loop que envia estado constantemente
async def broadcast_loop():
    while True:
        if connected:
            state = json.dumps({
                "type": "state",
                "players": players
            })

            await asyncio.gather(*[
                ws.send(state) for ws in connected
            ], return_exceptions=True)

        await asyncio.sleep(0.05)  # 20 vezes por segundo

PORT = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print(f"Servidor rodando na porta {PORT}")
        
        await asyncio.gather(
            broadcast_loop(),
            asyncio.Future()
        )

if __name__ == "__main__":
    asyncio.run(main())

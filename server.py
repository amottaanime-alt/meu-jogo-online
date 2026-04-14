import asyncio
import websockets
import json
import os

from db import init_db, register, login, save_position

init_db()

players = {}
connected = {}  # websocket -> player_id


# =========================
# BROADCAST LOOP
# =========================
async def broadcast_loop():
    while True:
        if connected:
            state = json.dumps({
                "type": "state",
                "players": players
            })

            await asyncio.gather(
                *[ws.send(state) for ws in connected.keys()],
                return_exceptions=True
            )

        await asyncio.sleep(0.05)


# =========================
# HANDLER
# =========================
async def handler(websocket):
    player_id = None

    try:
        async for message in websocket:
            data = json.loads(message)

            # =====================
            # REGISTER
            # =====================
            if data["type"] == "register":
                success = register(data["username"], data["password"])

                await websocket.send(json.dumps({
                    "type": "register_result",
                    "success": success
                }))


            # =====================
            # LOGIN
            # =====================
            elif data["type"] == "login":
                result = login(data["username"], data["password"])

                if result:
                    player_id = result["id"]

                    players[player_id] = {
                        "x": result["x"],
                        "y": result["y"]
                    }

                    connected[websocket] = player_id

                    await websocket.send(json.dumps({
                        "type": "login_success",
                        "id": player_id,
                        "x": result["x"],
                        "y": result["y"]
                    }))
                else:
                    await websocket.send(json.dumps({
                        "type": "login_failed"
                    }))


            # =====================
            # MOVE
            # =====================
            elif data["type"] == "move" and player_id:
                x = data["x"]
                y = data["y"]

                players[player_id]["x"] = x
                players[player_id]["y"] = y

                # salva no banco (persistência)
                save_position(player_id, x, y)


    except:
        pass

    finally:
        if player_id:
            players.pop(player_id, None)

        connected.pop(websocket, None)


# =========================
# START SERVER
# =========================
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

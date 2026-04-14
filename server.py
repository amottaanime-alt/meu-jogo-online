import asyncio
import websockets
import json
import os

from db import init_db, register, login, save_position

init_db()

players = {}
connections = {}  # websocket -> player_id


# =========================
# BROADCAST LOOP
# =========================
async def broadcast_loop():
    while True:
        if connections:
            state = json.dumps({
                "type": "state",
                "players": players
            })

            await asyncio.gather(
                *[ws.send(state) for ws in connections.keys()],
                return_exceptions=True
            )

        await asyncio.sleep(0.05)


# =========================
# HANDLER
# =========================
async def handler(websocket):
    player_id = None

    print("🟢 CONNECTED")

    try:
        async for message in websocket:

            print("📩 RAW MESSAGE:", message)

            data = json.loads(message)

            # =====================
            # REGISTER
            # =====================
            if data.get("type") == "register":

                username = data.get("username")
                password = data.get("password")

                print("🧾 REGISTER REQUEST:", username, password)

                success = register(username, password)

                await websocket.send(json.dumps({
                    "type": "register_result",
                    "success": success
                }))


            # =====================
            # LOGIN
            # =====================
            elif data.get("type") == "login":

                username = data.get("username")
                password = data.get("password")

                result = login(username, password)

                if result:
                    player_id = result["id"]

                    players[player_id] = {
                        "x": result["x"],
                        "y": result["y"]
                    }

                    connections[websocket] = player_id

                    await websocket.send(json.dumps({
                        "type": "login_success",
                        "id": player_id,
                        "x": result["x"],
                        "y": result["y"]
                    }))

                    print("✅ LOGIN OK:", player_id)

                else:
                    print("❌ LOGIN FAIL")

                    await websocket.send(json.dumps({
                        "type": "login_failed"
                    }))


            # =====================
            # MOVE
            # =====================
            elif data.get("type") == "move" and player_id:

                x = data.get("x")
                y = data.get("y")

                players[player_id] = {"x": x, "y": y}

                save_position(player_id, x, y)


    except Exception as e:
        print("❌ ERROR:", repr(e))

    finally:
        print("🔴 DISCONNECT")

        if player_id:
            players.pop(player_id, None)

        connections.pop(websocket, None)


# =========================
# START SERVER
# =========================
PORT = int(os.environ.get("PORT", 10000))


async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print("🚀 SERVER RUNNING")

        await asyncio.gather(
            broadcast_loop(),
            asyncio.Future()
        )


if __name__ == "__main__":
    asyncio.run(main())

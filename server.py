import asyncio
import websockets
import json
import uuid
import os

from world.entity_manager import EntityManager
from entities.player import Player

# =========================
# WORLD STATE (ENTITY SYSTEM)
# =========================
entity_manager = EntityManager()

connected = set()


# =========================
# WEBSOCKET HANDLER
# =========================
async def handler(websocket):
    player_id = str(uuid.uuid4())

    # cria entidade player
    player = Player(player_id, 100, 100)
    entity_manager.add(player)

    connected.add(websocket)

    try:
        # envia id pro client
        await websocket.send(json.dumps({
            "type": "init",
            "id": player_id
        }))

        async for message in websocket:
            data = json.loads(message)

            # =========================
            # MOVIMENTO DO PLAYER
            # =========================
            if data["type"] == "move":
                player = entity_manager.get(player_id)

                if player:
                    player.x = data["x"]
                    player.y = data["y"]

            # =========================
            # MONTA STATE DO MUNDO
            # =========================
            state = json.dumps({
                "type": "state",
                "players": {
                    eid: {
                        "x": entity.x,
                        "y": entity.y
                    }
                    for eid, entity in entity_manager.entities.items()
                }
            })

            # envia pra todos
            await asyncio.gather(*[
                ws.send(state) for ws in connected
            ])

    except:
        pass

    finally:
        connected.remove(websocket)

        # remove entidade do mundo
        entity_manager.remove(player_id)


# =========================
# SERVER START
# =========================
PORT = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print(f"Servidor rodando na porta {PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

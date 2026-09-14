import asyncio
import websockets

async def main():
    uri = "ws://192.168.180.129:8000/ws/terminal/wstestuser"
    async with websockets.connect(uri) as ws:
        await ws.send("echo hello_from_terminal\n")
        for _ in range(5):
            data = await ws.recv()
            print(repr(data))

asyncio.run(main())

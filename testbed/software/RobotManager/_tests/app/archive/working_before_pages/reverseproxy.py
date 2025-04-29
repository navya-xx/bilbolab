import asyncio
from aiohttp import web, ClientSession, ClientWebSocketResponse
import socket

HOSTNAME_TO_PORT = {
    "app1.local": 9001,
    "app2.local": 9002,
    "app3.local": 9003,
}


async def handle_proxy(request):
    hostname = request.headers.get("Host", "")
    port = HOSTNAME_TO_PORT.get(hostname)

    if not port:
        return web.Response(status=502, text=f"Unknown host: {hostname}")

    if request.headers.get("Upgrade", "").lower() == "websocket":
        # Handle WebSocket upgrade
        ws_server = web.WebSocketResponse()
        await ws_server.prepare(request)

        ws_url = f"http://127.0.0.1:{port}{request.rel_url}"
        async with ClientSession() as session:
            async with session.ws_connect(ws_url.replace("http", "ws")) as ws_client:

                async def ws_forward(ws_from, ws_to):
                    async for msg in ws_from:
                        message_type = msg.type
                        if message_type == web.WSMsgType.TEXT:
                            await ws_to.send_str(msg.data)
                        elif message_type == web.WSMsgType.BINARY:
                            await ws_to.send_bytes(msg.data)
                        elif message_type == web.WSMsgType.CLOSE:
                            await ws_to.close()
                        elif message_type == web.WSMsgType.ERROR:
                            break

                await asyncio.gather(
                    ws_forward(ws_server, ws_client),
                    ws_forward(ws_client, ws_server)
                )
        return ws_server

    # Regular HTTP forward
    target_url = f"http://127.0.0.1:{port}{request.rel_url}"
    async with ClientSession() as session:
        async with session.request(
                method=request.method,
                url=target_url,
                headers=request.headers,
                data=await request.read()
        ) as resp:
            body = await resp.read()
            return web.Response(
                status=resp.status,
                body=body,
                headers=resp.headers
            )


async def start_reverse_proxy():
    app = web.Application()
    app.router.add_route('*', '/{tail:.*}', handle_proxy)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=80)
    await site.start()
    print("🔁 Reverse proxy listening on port 80")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(start_reverse_proxy())
    except PermissionError:
        print("❌ You need sudo to bind to port 80 on macOS/Linux")

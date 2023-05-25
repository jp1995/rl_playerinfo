from logging_setup import log
import asyncio


async def handle_plugin(reader, writer, q):
    data = b''
    while True:
        chunk = await reader.read(64)
        if not chunk:
            writer.close()
            break
        data += chunk
    q.put(data)


async def serve(q):
    HOST = ''
    PORT = 8371
    server = await asyncio.start_server(lambda r, w: handle_plugin(r, w, q), HOST, PORT)
    addr = server.sockets[0].getsockname()
    log.info(f'Awaiting plugin on {addr}')

    async with server:
        await server.serve_forever()


def run_tcp_server(q):
    asyncio.run(serve(q))

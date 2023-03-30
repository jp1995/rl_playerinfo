import asyncio

async def handle_plugin(reader, writer, q):
    data = await reader.read(1024)
    q.put(data)

async def serve(q):
    HOST = ''
    PORT = 8371
    server = await asyncio.start_server(lambda r, w: handle_plugin(r, w, q), HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f'Awaiting plugin on {addr}')

    async with server:
        await server.serve_forever()

def run_tcp_server(q):
    asyncio.run(serve(q))

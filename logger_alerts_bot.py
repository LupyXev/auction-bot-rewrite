import asyncio, discord, discord.ext.tasks, socket
import struct
import pickle
import logging

client = discord.Client()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')



async def handle_client(sock_client):
    log_channel = client.get_channel(813801717572960316)
    while True:
        try:
            resp = await client.loop.sock_recv(sock_client, 4)
            slen = struct.unpack(">L", resp)[0]
        except struct.error as e:
            # Less than 4 bytes received
            break

        try:
            chunk = sock_client.recv(slen)
        except:
            print("ERROR")
            break

        if not chunk:
            break

        record = logging.makeLogRecord(pickle.loads(chunk))
        try:
            await log_channel.send(formatter.format(record))
        except:
            await log_channel.send("An error occured")
    """print("connection established")
    while True:
        resp = await client.loop.sock_recv(sock_client, 99999)
        print(resp.decode("utf-8"))
"""

async def listening():
    print("starting listening...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5060))
    server.listen()
    server.setblocking(False)

    loop = client.loop

    while True:
        sock_client, _ = await loop.sock_accept(server)
        loop.create_task(handle_client(sock_client))


"""a = client.loop.run_until_complete(client.loop.create_server(asyncio.Protocol, host='localhost', port=5060))
client.loop.run_until_complete(a.serve_forever())"""


listening_loop = discord.ext.tasks.Loop(listening, 0, 0, 0, None, True, client.loop)
listening_loop.start()

client.run("ODk2MDcyODYzNTQxNTE0MzMw.YWBy4g.sbu-3Sa0rLwpp7pbuV91fbyrALk")
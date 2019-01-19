import asyncio


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

def process_data(msg, metric_dict):
    if msg.find('\n') + 1 != len(msg):
        return 'error\nwrong command\n\n'

    parsed = msg.split()
    if len(parsed) == 2:
        get, metric = parsed
        if not get == "get":
            return 'error\nwrong command\n\n'

        answ = str()
        answ += 'ok\n'

        if metric == '*':
            for metric, l in metric_dict.items():
                for val, timestamp in l:
                    answ += f'{metric} {val} {timestamp}\n'
        else:
            for val, timestamp in metric_dict.get(metric, []):
                answ += f'{metric} {val} {timestamp}\n'

        answ += '\n'

        return answ

    elif len(parsed) == 4:
        put, metric, val, timestamp = parsed
        if not put == "put":
            return 'error\nwrong command\n\n'

        val, timestamp = float(val), int(timestamp)

        if metric in metric_dict:
            for v, t in metric_dict[metric]:
                if t == timestamp:
                    metric_dict[metric].remove((v, t))
                    break

        metric_dict.setdefault(metric, []).append((val, timestamp))

        return 'ok\n\n'

    else:
        return 'error\nwrong command\n\n'

metric_dict = dict()

class ClientServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        resp = process_data(data.decode(), metric_dict)
        self.transport.write(resp.encode())


if __name__ == '__main__':
    run_server('127.0.0.1', 8888)

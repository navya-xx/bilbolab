import random
import time

from core.utils.websockets.websockets import SyncWebsocketServer


def main():
    server = SyncWebsocketServer(host='127.0.0.1', port=8080)

    server.start()

    x = 1
    y = 2

    while True:
        data = {
            'key1': x,
            'key2': y
        }
        server.send(data)
        x += 0.1 + random.randint(-10,10)
        y += 0.1 + random.randint(-10,10)
        time.sleep(0.1)


if __name__ == '__main__':
    main()

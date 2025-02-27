import time

from utils.websockets.websockets import SyncWebsocketServer


def main():
    server = SyncWebsocketServer(host='127.0.0.1', port=8000)
    server.start()

    data = {
        'a': 1,
        'b': "Hello"
    }

    while True:
        server.send(data)
        data['a'] += 1
        time.sleep(1)


if __name__ == '__main__':
    main()

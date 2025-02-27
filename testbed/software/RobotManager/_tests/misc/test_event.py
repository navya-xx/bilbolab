import threading
import time

from utils.events import ConditionEvent


class Sender:
    def __init__(self):
        self.event = ConditionEvent()
        self.thread = threading.Thread(target=self.task, daemon=True)
        self.data = {
            'x': 0,
            'y': "HALLO",
        }

    def start(self):
        print("Starting Sender")
        self.thread.start()

    def task(self):
        while True:
            print("Sender: Sending event")
            self.data['x'] += 1
            self.event.set(resource=self.data)
            time.sleep(2)


class Waiter:

    def __init__(self, id, sender):
        self.sender = sender
        self.id = id
        self.thread = threading.Thread(target=self.task, daemon=True)

    def start(self):
        print(f"Starting Waiter {self.id}")
        self.thread.start()

    def task(self):
        while True:
            print(f"Waiter {self.id}: Waiting for event")
            if self.sender.event.wait(timeout=5):
                value = self.sender.event.get_data()
                print(f"Event received. Value: {value}")
            else:
                print(f"Waiter {self.id}: Timeout")


def main():
    sender = Sender()
    waiter = Waiter(1, sender)
    waiter.start()
    sender.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

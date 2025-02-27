import threading
import time


class ProducerClass:
    sample: dict

    def __init__(self):
        self.sample = {}
        self.x = 1
        self.thread = threading.Thread(target=self.task, daemon=True)
        self.condition = threading.Condition()

    def start(self):
        self.thread.start()

    def task(self):

        while True:
            with self.condition:
                self.sample['x'] = self.x
                self.sample['y'] = 3
                self.condition.notify_all()
            self.x += 1
            time.sleep(1)

class ConsumerClass:

    def __init__(self, producer: ProducerClass, name: str):
        self.thread = threading.Thread(target=self.task, daemon=True)
        self.name = name
        self._producer = producer

    def start(self):
        self.thread.start()

    def task(self):
        while True:
            with self._producer.condition:
                self._producer.condition.wait()
                print(f"{self.name}: {self._producer.sample}")


def main():
    producer = ProducerClass()
    consumer1 = ConsumerClass(producer, "Consumer 1")
    consumer2 = ConsumerClass(producer, "Consumer 2")
    consumer1.start()
    consumer2.start()
    producer.start()

    while True:
        time.sleep(10)



if __name__ == '__main__':
    main()
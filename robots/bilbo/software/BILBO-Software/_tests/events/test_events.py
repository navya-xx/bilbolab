import dataclasses

from utils.callbacks import Callback
from utils.dataclass_utils import freeze_dataclass_instance
from utils.events import ConditionEvent, EventListener
import threading
import time


@dataclasses.dataclass
class EventData:
    x: float = 1.0
    y: float = 2.0

class Producer:
    def __init__(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.event = ConditionEvent()
        self.data = [1, 2, 3, 4, 5]

    def start(self):
        self.thread.start()

    def _run(self):
        while True:
            print(f"Producer: Sending event")
            self.event.set(freeze_dataclass_instance(EventData()))
            # self.data += 1
            time.sleep(1)
    
class Consumer:
    def __init__(self, producer: Producer, id):
        self.producer = producer
        self.id = id
        self.thread = threading.Thread(target=self._consume, daemon=True)

    def start(self):
        self.thread.start()

    def _consume(self):
        while True:
            x = self.producer.event.wait()  # Wait for the ConditionEvent
            # with self.producer.event.resource:
            #     x = self.producer.event.resource.get()
            print(f"Consumer {self.id}: Event {x} received\n")


def test(*args, **kwargs):
    print("HALLO")

def main():
    producer = Producer()
    listener = EventListener(producer.event, callback=Callback(function=test), once=False)
    listener.start()
    # consumer1 = Consumer(id=1, producer=producer)
    # consumer2 = Consumer(id=2, producer=producer)


    # consumer1.start()
    # consumer2.start()
    producer.start()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
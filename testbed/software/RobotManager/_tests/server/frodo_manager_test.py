import time

from robots.frodo.frodo import Frodo
from robots.frodo.frodo_manager import FrodoManager


def main():
    active_frodo: Frodo = None

    def rx_stream_callback(data, *args, **kwargs):
        print(f"rx_stream_callback: {data}")

    def new_robot_callback(robot: Frodo, *args, **kwargs):
        print(f"new robot: {robot.id}")
        nonlocal active_frodo
        active_frodo = robot
        active_frodo.callbacks.stream.register(rx_stream_callback)

    manager = FrodoManager()

    manager.callbacks.new_robot.register(
        new_robot_callback
    )

    manager.init()
    manager.start()

    while True:

        if active_frodo is not None:
            data = active_frodo.getData()

        time.sleep(0.1)


if __name__ == '__main__':
    main()

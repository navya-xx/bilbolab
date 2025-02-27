import time

from utils.exit import ExitHandler


class ClassA:
    exit: ExitHandler

    def __init__(self):
        self.exit = ExitHandler()
        self.exit.register(self.on_exit)

    def on_exit(self, *args, **kwargs):
        print("Exiting Class A")


class ClassB:
    exit: ExitHandler

    def __init__(self):
        self.exit = ExitHandler()
        self.exit.register(self.on_exit)

    def on_exit(self, *args, **kwargs):
        print("Exiting Class B")


def main():
    a = ClassA()
    b = ClassB()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

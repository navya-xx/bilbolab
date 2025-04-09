import time

from core.utils.callbacks import Callback
from core.utils.thread_worker import ThreadWorker, WorkerPool


def testfunction1(input: int, *args, **kwargs):
    # raise Exception("Test Exception")
    time.sleep(0.5)
    return input*2


def listener_callback(*args, **kwargs):
    print("Listener callback")


def main():
    num_workers = 10
    workers = []

    for i in range(0, num_workers):
        workers.append(ThreadWorker(start=False, function=Callback(function=testfunction1, parameters={'input': i})))

    pool = WorkerPool(workers)


    for i in range(0, 3):
        pool.start()
        results = pool.wait(timeout=1)
        data = pool.get_data()
        print(f"Run Time: {pool.run_time} ms")
        if all(results):
            print(f"All workers finished in time: {results}")
            print(f"Errors: {pool.errors}")
            print(f"Data: {data}")
        else:
            print(f"Not all workers finished successfully: {results}")
            print(f"Errors: {pool.errors}")
            print(f"Data: {data}")

        pool.reset()
        time.sleep(3)


if __name__ == '__main__':
    main()

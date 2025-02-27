import threading
import time
from threading import Timer as ThreadTimer

from utils.callbacks import Callback


def time_ms():
    return int(time.time_ns() / 1000)


class IntervalTimer:
    """
    A timer utility to handle fixed-interval loop timing.
    Automatically calculates and aligns to the next interval based on a start time.
    """

    def __init__(self, interval: float):
        self.interval = interval
        self.previous_time = time.perf_counter()

    def sleep_until_next(self):
        """
        Sleeps until the next interval is reached, starting from the last recorded time.
        Automatically updates the internal time reference.
        """
        target_time = self.previous_time + self.interval
        current_time = time.perf_counter()
        remaining = target_time - current_time

        if remaining <= 0:
            raise Exception("Race Conditions")

        if remaining > 0:
            precise_sleep(remaining)

        self.previous_time = target_time  # Update for the next cycle

    def reset(self):
        """
        Resets the internal timer to the current time.
        """
        self.previous_time = time.perf_counter()


def precise_sleep(seconds: float):
    """
    High-precision sleep function.
    """
    target_time = time.perf_counter() + seconds

    # Coarse sleep until close to the target time
    while True:
        remaining = target_time - time.perf_counter()
        if remaining <= 0:
            break
        if remaining > 0.001:  # If more than 1ms remains, sleep briefly
            time.sleep(remaining / 2)  # Use fractional sleep to avoid overshooting
        else:
            break

    # Busy-wait for the final few microseconds
    while time.perf_counter() < target_time:
        pass


class Timer:
    _reset_time: float

    timeout: float
    repeat: bool

    _callbacks: dict[str, list]
    _threadTimer: ThreadTimer

    _stop: bool

    def __init__(self, initial_time = 0):
        self._reset_time = time.time()

        self.set(initial_time)
        self.timeout = None
        self.repeat = False

        self._threadTimer = None

        self._callbacks = {
            'timeout': []
        }

    # ------------------------------------------------------------------------------------------------------------------
    def registerCallback(self, callback_id, function: callable, parameters: dict = None, lambdas: dict = None,
                         **kwargs):
        callback = Callback(function, parameters, lambdas, **kwargs)

        if callback_id in self._callbacks:
            self._callbacks[callback_id].append(callback)
        else:
            raise Exception("Invalid Callback type")

    # ------------------------------------------------------------------------------------------------------------------

    def start(self, timeout=None, repeat: bool = True):
        self.reset()

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def time(self):
        return time.time() - self._reset_time

    # ------------------------------------------------------------------------------------------------------------------
    def reset(self):
        self._reset_time = time.time()
        if self._threadTimer is not None:
            self._threadTimer.cancel()
            self._threadTimer = ThreadTimer(self.timeout, self._timeout_callback)
            self._threadTimer.start()

    # ------------------------------------------------------------------------------------------------------------------
    def stop(self):
        self._threadTimer.cancel()
        self._threadTimer = None

    # ------------------------------------------------------------------------------------------------------------------
    def set(self, value):
        self._reset_time = time.time() - value

    def _timeout_callback(self):
        for callback in self._callbacks['overflow']:
            callback()

        if self.repeat:
            self._threadTimer = ThreadTimer(self.timeout, self._timeout_callback)
            self._threadTimer.start()
        else:
            self._threadTimer = None

    # ------------------------------------------------------------------------------------------------------------------
    def __gt__(self, other):
        return self.time > other

    # ------------------------------------------------------------------------------------------------------------------
    def __lt__(self, other):
        return self.time < other


# ======================================================================================================================
class TimeoutTimer:
    def __init__(self, timeout_time, timeout_callback):
        """
        Initializes the TimeoutTimer.

        :param timeout_time: The timeout duration in seconds.
        :param timeout_callback: The callback function to execute on timeout.
        """
        self.timeout_time = timeout_time
        self.timeout_callback = timeout_callback
        self._last_reset_time = None  # Will track the last reset time
        self._stop_event = threading.Event()
        self._is_running = threading.Event()  # Controls whether the timer is counting
        self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self._timer_thread.start()

    def _run_timer(self):
        """The method executed by the timer thread."""
        while not self._stop_event.is_set():
            # Timer logic only executes if the timer is in a running state
            if self._is_running.is_set():
                if self._last_reset_time is not None and time.time() - self._last_reset_time >= self.timeout_time:
                    # Timer has timed out; trigger the callback and enter timeout state
                    self.timeout_callback()
                    self._is_running.clear()  # Exit the running state
            time.sleep(0.1)  # Small sleep to avoid high CPU usage.

    def start(self):
        """
        Starts the timer. If already running, it continues without resetting the time.
        """
        print("Start the timer")
        if not self._is_running.is_set():
            self._is_running.set()
            self._last_reset_time = time.time()

    def reset(self):
        """
        Resets the timer by updating the last reset time.
        """
        print("Reset")
        if self._is_running.is_set():
            self._last_reset_time = time.time()

    def stop(self):
        """
        Stops the timer (ends the running state but keeps the thread alive).
        """
        self._is_running.clear()

    def close(self):
        """
        Fully stops the timer thread and terminates it.
        """
        self._stop_event.set()
        self._timer_thread.join()
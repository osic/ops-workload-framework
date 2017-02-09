import time


class Stopwatch(object):

    def __init__(self):
        """Initialize a new `Stopwatch`, but do not start timing."""
        self.start_time = None
        self.stop_time = None

    def start(self):
        """Start timing."""
        self.start_time = time.time()

    def stop(self):
        """Stop timing."""
        self.stop_time = time.time()

    @property
    def time_elapsed(self):
        """Return the number of seconds that have elapsed since this
        `Stopwatch` started timing.

        This is used for checking how much time has elapsed while the timer is
        still running.
        """
        assert not self.stop_time, \
            "Can't check `time_elapsed` on an ended `Stopwatch`."
        return time.time() - self.start_time

    @property
    def total_run_time(self):
        """Return the number of seconds that elapsed from when this `Stopwatch`
        started to when it ended.
        """
        return self.stop_time - self.start_time

    def __enter__(self):
        """Start timing and return this `Stopwatch` instance."""
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        """Stop timing.

        If there was an exception inside the `with` block, re-raise it.

        >>> with Stopwatch() as stopwatch:
        ...     raise Exception
        Traceback (most recent call last):
            ...
        Exception
        """
        self.stop()
        if type:
            raise type, value, traceback

from contextlib import contextmanager
import time


clock = time.perf_counter


class Console(object):
    def __init__(self, verbosity=1, print=print):
        self.verbosity = verbosity
        self.__print = print

    @classmethod
    def of(cls, obj):
        if obj is None:
            return cls()
        elif isinstance(obj, cls):
            return obj
        elif isinstance(obj, int):
            return cls(obj)
        elif callable(obj):
            return cls(1, obj)
        else:
            raise NotImplementedError

    def __getitem__(self, verbosity):
        return Console(self.verbosity + verbosity, self.__print)

    def __bool__(self):
        return self.verbosity > 0

    def print(self, *args, **kwargs):
        if self and self.__print:
            self.__print(*args, **kwargs)

    @contextmanager
    def timed(self, start_text=None, stop_text=None):
        started = clock()
        if self and start_text:
            self.print(start_text)

        yield

        elapsed = clock() - started
        if self and stop_text:
            self.print(stop_text.format(elapsed))

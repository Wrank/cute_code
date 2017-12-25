# -*- coding:utf-8 -*-

import collections
import functools
import time


class RateLimiter(object):

    def __init__(self, max_calls, period=1.0, callback=None):
        self.calls = collections.deque()
        self.period = period
        self.max_calls = max_calls
        self.callback = callback

    def __call__(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                if not self.exceed:
                    return f(*args, **kwargs)
                if self.callback is not None:
                    self.callback(self.period)
                    return f(*args, **kwargs)
                raise Exception("rate exceed")

        return wrapped

    def __enter__(self):
        if self.exceed:
            if self.callback is not None:
                self.callback(self.period)
                return self
            else:
                raise Exception("rate exceed")

        return self

    @property
    def exceed(self):
        return len(self.calls) > (self.max_calls - 1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.calls.append(time.time())
        while self._timespan >= self.period:
            self.calls.popleft()

    @property
    def _timespan(self):
        return self.calls[-1] - self.calls[0]

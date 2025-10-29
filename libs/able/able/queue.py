import threading
from functools import wraps, partial
try:
    from queue import Empty, Queue
except ImportError:
    from Queue import Empty, Queue
from kivy.clock import Clock
from kivy.logger import Logger


def ble_task(method):
    """
    Enque method
    """
    @wraps(method)
    def wrapper(obj, *args, **kwargs):
        task = partial(method, obj, *args, **kwargs)
        obj.queue.enque(task)
    return wrapper


def ble_task_done(method):
    @wraps(method)
    def wrapper(obj, *args, **kwargs):
        obj.queue.done(*args, **kwargs)
        method(obj, *args, **kwargs)
    return wrapper


def with_lock(method):
    @wraps(method)
    def wrapped(obj, *args, **kwargs):
        locked = obj.lock.acquire(False)
        if locked:
            try:
                return method(obj, *args, **kwargs)
            finally:
                obj.lock.release()
    return wrapped


class BLEQueue(object):

    def __init__(self, timeout=0):
        self.lock = threading.Lock()
        self.ready = True
        self.queue = Queue()
        self.set_timeout(timeout)

    def set_timeout(self, timeout):
        Logger.debug("set queue timeout to {}".format(timeout))
        self.timeout = timeout
        self.timeout_event = Clock.schedule_once(
            self.on_timeout, self.timeout or 0)
        self.timeout_event.cancel()

    def enque(self, task):
        queue = self.queue
        if self.timeout == 0:
            self.execute_task(task)
        else:
            queue.put_nowait(task)
            self.execute_next()

    @with_lock
    def execute_next(self, ready=False):
        if ready:
            self.ready = True
        elif not self.ready:
            return
        try:
            task = self.queue.get_nowait()
        except Empty:
            return
        self.ready = False
        if task is not None:
            self.execute_task(task)

    def done(self, *args, **kwargs):
        self.timeout_event.cancel()
        self.ready = True
        self.execute_next()

    def on_timeout(self, *args, **kwargs):
        self.done()

    def execute_task(self, task):
        if self.timeout and self.timeout_event:
            self.timeout_event()
        task()

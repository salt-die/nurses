from collections import deque
from heapq import heappop, heappush
from textwrap import dedent
from time import sleep, time
from types import coroutine


class Task:
    __slots__ = "coro", "is_canceled", "deadline"

    def __init__(self, coro):
        self.coro = coro
        self.is_canceled = False

    def cancel(self):
        self.is_canceled = True

    def __lt__(self, other):
        return self.deadline < other.deadline


class Scheduler:
    __slots__ = "tasks", "ready", "sleeping", "current"

    def __init__(self):
        self.tasks = { }
        self.ready = deque()
        self.sleeping = [ ]
        self.current = None

    async def sleep(self, delay):
        self.current.deadline = time() + delay
        heappush(self.sleeping, self.current)
        self.tasks[self.current.coro] = self.current
        self.current = None
        await self.next_task()

    def run_soon(self, *coros):
        """Schedule the given coroutines to run as soon as possible.
        """
        for coro in coros:
            self.new_task(coro)

    def new_task(self, coro):
        """Schedule a given coroutine and return a :class: Task.  `task.cancel()` will unschedule the coroutine.
        """
        self.tasks[coro] = task = Task(coro)
        self.ready.append(task)
        return task

    def run(self, *coros):
        """Start the event loop. All of `coros` will be scheduled with `run_soon` before the loop starts.
        """
        self.run_soon(*coros)

        ready = self.ready
        sleeping = self.sleeping
        tasks = self.tasks

        while ready or sleeping:
            now = time()

            while sleeping and sleeping[0].deadline <= now:
                ready.append(heappop(sleeping))

            if ready:
                self.current = ready.popleft()
            else:
                self.current = heappop(sleeping)
                sleep(self.current.deadline - now)

            del tasks[self.current.coro]

            if self.current.is_canceled:
                continue

            try:
                self.current.coro.send(None)
            except StopIteration:
                continue

            if self.current:
                ready.append(self.current)
                tasks[self.current.coro] = self.current

    def aiter(self, iterable, *args, delay=0, n=0, **kwargs):
        """Utility function: wraps a callable in a coroutine or creates an async iterator from an iterable.
        """
        if callable(iterable):
            loop = f"for _ in range({n})" if n else "while True"
            body = "iterable(*args, **kwargs)"
        else:
            loop = "for i in iterable"
            body = "yield i"

        awaitable=f"self.sleep({delay})" if delay > 0 else "self.next_task()"

        code = f"""
            async def wrapped():
                {loop}:
                    {body}
                    await {awaitable}
        """

        exec(dedent(code), locals(), loc := { })
        return loc["wrapped"]()

    def schedule(self, callable, *args, delay=0, n=0, **kwargs):
        """
        Schedule `callable(*args, **kwargs)` every `delay` seconds.
        Returns a :class: Task (task.cancel() can be used to unschedule `callable`).

        If `n` is non-zero, `callable` is only scheduled `n` times.
        """
        return self.new_task(self.aiter(callable, *args, delay=delay, n=n, **kwargs))

    @staticmethod
    @coroutine
    def next_task():
        yield

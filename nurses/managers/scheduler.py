from collections import deque
from heapq import heappop, heappush
from textwrap import dedent
from time import sleep, monotonic
from types import coroutine


class Task:
    __slots__ = "scheduler", "coro", "is_canceled", "deadline", "is_rescheduled"

    def __init__(self, scheduler, coro):
        self.scheduler = scheduler
        self.coro = coro
        self.is_canceled = False
        self.is_rescheduled = False

    def cancel(self):
        self.is_canceled = True

    def __call__(self):
        """
        Reschedule this task as a new task. Returns the new task.

        Notes
        -----
        To reschedule a task, the task must be canceled. A task can only be rescheduled once.
        (use the returned task to cancel and reschedule the wrapped coroutine again)

        Raises
        ------
        RuntimeError
            If the task isn't canceled or if task has already been rescheduled.
        """
        if not self.is_canceled:
            raise RuntimeError("task already scheduled")

        if self.is_rescheduled:
            raise RuntimeError("task already rescheduled")

        self.is_rescheduled = True
        return self.scheduler.new_task(self.coro)

    def __lt__(self, other):
        return self.deadline < other.deadline


class Scheduler:
    __slots__ = "ready", "sleeping", "current"

    def __init__(self):
        self.ready = deque()
        self.sleeping = [ ]
        self.current = None

    async def sleep(self, delay):
        self.current.deadline = monotonic() + delay
        heappush(self.sleeping, self.current)
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
        self.ready.append(Task(self, coro))
        return self.ready[-1]

    def run(self, *coros):
        """Start the event loop. All of `coros` will be scheduled with `run_soon` before the loop starts.
        """
        self.run_soon(*coros)

        ready = self.ready
        sleeping = self.sleeping

        while ready or sleeping:
            now = monotonic()

            while sleeping and sleeping[0].deadline <= now:
                ready.append(heappop(sleeping))

            if ready:
                self.current = ready.popleft()
            else:
                self.current = heappop(sleeping)
                sleep(self.current.deadline - now)

            if self.current.is_canceled:
                continue

            try:
                self.current.coro.send(None)
            except StopIteration:
                continue

            if self.current:
                ready.append(self.current)

    def aiter(self, iterable, *args, delay=0, n=0, **kwargs):
        """Utility function: wraps a callable in a coroutine or creates an async iterator from an iterable.
        """
        if callable(iterable):
            loop = f"for _ in range({n})" if n else "while True"
            body = "iterable(*args, **kwargs)"
        else:
            loop = "for i in iterable"
            body = "yield i"

        awaitable = f"self.sleep({delay})" if delay > 0 else "self.next_task()"

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

from collections import deque
from heapq import heappop as pop, heappush as push
from time import sleep, time


class next_task:
    __slots__ = ()

    def __await__(self):
        yield


class Task:
    __slots__ = "coro", "is_canceled", "deadline"

    def __init__(self, coro, deadline=0):
        self.coro = coro
        self.deadline = deadline
        self.is_canceled = False

    def __lt__(self, other):
        return self.deadline < other.deadline


class Scheduler:
    def __init__(self):
        self.tasks = { }
        self.ready = deque()
        self.sleeping = [ ]
        self.current = None

    async def sleep(self, delay):
        self.current.deadline = time() + delay
        push(self.sleeping, self.current)
        self.tasks[self.current.coro] = self.current
        self.current = None
        await next_task()

    def cancel(self, coro):
        self.tasks[coro].is_canceled = True

    def run_soon(self, *coros):
        for coro in coros:
            self.tasks[coro] = task = Task(coro)
            self.ready.append(task)

    def run(self, *coros):
        self.run_soon(*coros)

        ready = self.ready
        sleeping = self.sleeping
        tasks = self.tasks

        while ready or sleeping:
            now = time()

            while sleeping and sleeping[0].deadline <= now:
                ready.append(pop(sleeping))

            if ready:
                self.current = ready.popleft()
            else:
                self.current = pop(sleeping)
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

    def schedule_callback(self, callback, delay, *args, **kwargs):
        """
        Schedule `callback(*args, **kwargs)` every `delay` seconds.  `delay` can be 0.
        Returns a coroutine (this can be used to cancel the callback with `cancel(coroutine)`).
        """
        async def wrapped():
            while True:
                callback(*args, **kwargs)
                if delay > 0:
                    await self.sleep(delay)
                else:
                    await next_task()

        coro = wrapped()
        self.run_soon(coro)
        return coro

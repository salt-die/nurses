from collections import deque
from heapq import heappop as pop, heappush as push
from itertools import count
from time import sleep, time


class next_task:
    def __await__(self):
        yield


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.sleeping = [ ]
        self.seq = count()
        self.current = None

    async def sleep(self, delay):
        push(self.sleeping, (time() + delay, next(self.seq), self.current))
        self.current = None
        await next_task()

    def run_soon(self, *coros):
        self.ready.extend(coros)

    def run(self):  # TODO: add getch and dispatch
        while self.ready or self.sleeping:
            if self.ready:
                self.current = self.ready.popleft()
            else:
                deadline, _, self.current = pop(self.sleeping)
                if (delta := deadline - time()) > 0:
                    sleep(delta)  # This blocks.  Once widgets can consume text or data from a queue this could be a bad idea.

            try:
                self.current.send(None)
            except StopIteration:
                pass
            else:
                if self.current:
                    self.ready.append(self.current)
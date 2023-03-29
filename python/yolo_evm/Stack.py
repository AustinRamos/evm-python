from sre_constants import MAX_REPEAT
from .constants import MAX_STACK_DEPTH, MAX_UINT256

class Stack:
    def __init__(self, max_depth=1024) -> None:
        self.stack = []
        self.max_depth = max_depth

    
    def push(self, item: int) -> None:
        if item < 0 or item > 2**256 - 1:
            raise InvalidStackItem({"item": item})

        if (len(self.stack) + 1) > self.max_depth:
            raise StackOverflow()

        self.stack.append(item)

    def pop(self) -> int:
        if len(self.stack) == 0:
            raise StackUnderflow()

        return self.stack.pop()


class StackUnderflow(Exception):
    ...


class StackOverflow(Exception):
    ...


class InvalidStackItem(Exception):
    ...
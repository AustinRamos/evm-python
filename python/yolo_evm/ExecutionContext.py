from inspect import stack
from .Memory import Memory
from .Stack import Stack

class ExecutionContext:
    def __init__(self,code=bytes(),stack=None ,pc=0, memory=Memory()) ->None:
        self.code = code
        self.stack = Stack()
        self.memory = memory
        self.pc = pc
        self.stopped = False
        self.returndata = bytes()

    def set_return_data(self,offset:int, length: int) -> None:
        self.stopped = True
        self.returndata= self.memory.load_range(offset,length)

    def stop(self) ->None:
        self.stopped = True
    def read_code(self, num_bytes) -> int:
        #returns next num_bytes from code buffer as int and advances pc

        value = int.from_bytes(self.code[self.pc : self.pc+num_bytes],byteorder="big")
        self.pc += num_bytes
        return value
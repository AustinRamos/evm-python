from inspect import stack
from .Memory import Memory
from .Stack import Stack

class InvalidCalldataAccess(Exception):
    ...



    #Execution contexts (caller, origin, balance, gas limit, etc)

    # A VM execution loop looks something like this:

    # Fetch the instruction the PC points to
    # Execute the instruction
    # If the instruction jumps, set the PC to the new target
    # Otherwise, increment the PC


#new memory area, seperate from main memory, stack, and code buffer
#how we access call data is by 3 opcodes:
# 1) CALLLDATALOAD 
# 2) CALLDATASIZE
# 3) CALLDATACOPY
class Calldata:
    def __init__(self, data=bytes()) -> None:
        self.data = data

    def __len__(self) -> int:
        return len(self.data)

    def read_byte(self,offset:int)-> int:
        if offset < 0:
            raise InvalidCalldataAccess({"offset":offset})
        return self.data[offset] if offset< len(self.data) else 0

    def read_word(self,offset:int) ->int:
        return int.from_bytes(
            [self.read_byte(x) for x in range[offset:offset+32]],"big"
        )

class ExecutionContext:
    def __init__(self,code=bytes(),stack=None ,pc=0, memory=Memory(),calldata=None) ->None:
        self.code = code
        self.stack = Stack()
        self.memory = memory
        self.pc = pc
        self.stopped = False
        self.returndata = bytes()
        self.calldata = calldata if calldata else Calldata ()

    def set_return_data(self,offset:int, length: int) -> None:
        self.stopped = True
        self.returndata= self.memory.load_range(offset,length)

    def set_program_counter(self, _pc:int) -> None:
        self.pc = _pc

    def stop(self) ->None:
        self.stopped = True
    def read_code(self, num_bytes) -> int:
        #returns next num_bytes from code buffer as int and advances pc

        value = int.from_bytes(self.code[self.pc : self.pc+num_bytes],byteorder="big")
        self.pc += num_bytes
        return value
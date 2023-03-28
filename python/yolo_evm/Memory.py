from .constants import MAX_UINT256, MAX_UINT8

class Memory:
    def __init__(self) -> None:
        self.memory = []

    def store(self, offset: int, value: int) -> None:
        if offset < 0 or offset > MAX_UINT256:
            raise InvalidMemoryAccess({"offset": offset, "value": value})

        if value < 0 or value > MAX_UINT8:
            raise InvalidMemoryValue({"offset": offset, "value": value})

        # expand memory if needed
        if offset >= len(self.memory):
            self.memory.extend([0] * (offset - len(self.memory) + 1))

        self.memory[offset] = value

    def load(self, offset: int) -> int:
        if offset < 0:
            raise InvalidMemoryAccess({"offset": offset})

        if offset >= len(self.memory):
            return 0

        return self.memory[offset]

    def load_range(self,offset, length):
            #we could use a slice here, but this lets us get 0 bytes if we read past the end of concrete memory 
        return bytes(self.load(x) for x in range(offset, offset+length))
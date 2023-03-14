from .constants import MAX_UINT256
from .ExecutionContext import ExecutionContext

class Instruction:
    def __init__(self, opcode: int, name: str):
        self.opcode = opcode
        self.name = name

    def execute(self, context: ExecutionContext) -> None:
        raise NotImplementedError

class UnknownOpcode(Exception):
    ...


class InvalidCodeOffset(Exception):
    ...


INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}


def register_instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func
    INSTRUCTIONS.append(instruction)

    assert opcode not in INSTRUCTIONS_BY_OPCODE
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction

    return instruction


STOP = register_instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
PUSH1 = register_instruction(
    0x60,
    "PUSH1",
    (lambda ctx: ctx.stack.push(ctx.read_code(1))),
)
ADD = register_instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) % 2 ** 256)),
)
MUL = register_instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) % 2 ** 256)),
)
# MSTore pops offst and word from stack, and stores lowest byte of that word in memory
MSTORE8 = register_instruction(
    0x53,
    "MSTORE8",
    (lambda ctx: ctx.memory.store(ctx.stack.pop(), ctx.stack.pop() % 256))
)

RETURN = register_instruction(
    0xF3,
    "RETURN",
    (lambda ctx: ctx.memory.load_range(ctx.stack.pop(),ctx.stack.pop()))
)


def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0:
        raise InvalidCodeOffset({"code": context.code.hex(), "pc": context.pc})

    # section 9.4.1 of the yellow paper, if pc is outside code, then the operation to be executed is STOP
    if context.pc >= len(context.code):
        return STOP

    opcode = context.read_code(1)
    instruction = INSTRUCTIONS_BY_OPCODE.get(opcode)
    if instruction is None:
        raise UnknownOpcode({"opcode": opcode})

    return instruction
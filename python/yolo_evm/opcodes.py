
from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Union
import sys
from exceptions import InvalidJumpDestination
from .constants import MAX_UINT256
from .ExecutionContext import ExecutionContext
import helpers 

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

class DuplicateOpcode(Exception):
    ...


class InstructionRegistry:
    def __init__(self):
        self.by_code = [None] * 256
        self.by_name = {}
        self.by_func = {}

    def __getitem__(self, item: Union[int, str, object]) -> Optional[Instruction]:
        if isinstance(item, int):
            retrieved = self.by_code[item]
            return retrieved

        if isinstance(item, str):
            return self.by_name[item]

        if callable(item):
            return self.by_func[item]

        raise TypeError(f"Unexpected type for instruction lookup: {type(item)}")

    def __iter__(self):
        return iter([i for i in self.by_code if i is not None])

    def __len__(self):
        return len(self.by_name)

    def add(self, instruction: Instruction):
        if self.by_code[instruction.opcode] is not None:
            raise DuplicateOpcode({"opcode": instruction.opcode})

        self.by_code[instruction.opcode] = instruction
        self.by_name[instruction.name] = instruction
        self.by_func[instruction.execute] = instruction


REGISTRY = InstructionRegistry()
INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}


def register_instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func
    INSTRUCTIONS.append(instruction)

    if opcode in INSTRUCTIONS_BY_OPCODE:
        raise DuplicateOpcode({"opcode": opcode})
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction

    return instruction


def assemble(instructions: Sequence[Union[Instruction, int, object]], print_bin=True) -> bytes:
    result = bytes()
    for item in instructions:
        if isinstance(item, Instruction):
            result += item.to_bytes()
        elif isinstance(item, int):
            result += int_to_bytes(item)
        elif callable(item):
            _instruction = REGISTRY[item]
            result += bytes([_instruction.opcode])
        elif isinstance(item, str):
            # assume this is our assembler syntax, as produced by disasm.py
            # e.g. <offset>: <OPCODE|UNKNOWN|DATA> [operand] [# comment]
            if item.startswith("#"):
                continue

            comment_start = item.find("#")
            if comment_start != -1:
                item = item[:comment_start]

            tokens = item.split(":", 2)
            if len(tokens) > 2:
                raise ValueError(f"Invalid item: {item}")
            elif len(tokens) == 2:
                offset_str, rest = item.split(":")
                offset = int(offset_str.strip(), 16)
                if offset != len(result):
                    # print to stderr
                    print(
                        f"Warning: expected to write at offset {offset_str}, but currently at {len(result):04x}",
                        file=sys.stderr,
                    )
            else:
                rest = item

            tokens = rest.strip().split(" ", 2)
            instruction_str = tokens[0].strip()
            if instruction_str == "UNKNOWN" or instruction_str == "DATA":
                hex_str = tokens[1].strip()
                result += bytes.fromhex(hex_str[2:] if hex_str.startswith("0x") else hex_str)

            else:
                instruction = REGISTRY[instruction_str]

                if not instruction:
                    raise ValueError(f"Unknown instruction {instruction_str}")

                result += instruction.opcode.to_bytes(1, "big")

                if len(tokens) > 1:
                    operand = tokens[1].strip()
                    result += bytes.fromhex(operand[2:] if operand.startswith("0x") else operand)

        else:
            raise TypeError(f"Unexpected {type(item)} in {instructions}")

    if print_bin:
        print(result.hex())

    return result

def swap(self,i: int) -> None:
    if len(self.stack) < i:
        raise StackUnderflow()
    self.stack[-1], self.stack[-i-1] = self.stack[-i-1],self.stack[-1]

def _do_jump(ctx:ExecutionContext, target_pc: int)->None:
    if target_pc not in ctx.jumpdests:
        raise InvalidJumpDestination(target_pc=target_pc,context=ctx)

def execute_SUB(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push((a - b) % 2 ** 256)



def execute_JUMP(ctx: ExecutionContext)->None:
    _do_jump(ctx,ctx.stack.pop())

def execute_JUMPI(ctx: ExecutionContext)->None:
    target_pc,cond = ctx.stack.pop(),ctx.stack.pop()

    if cond !=0:
        _do_jump(ctx,target_pc)


STOP = register_instruction(0x00, "STOP", (lambda ctx: ctx.stop()))

ADD = register_instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) % 2 ** 256)),
)

SUB = register_instruction(
    0x03,
    "SUB",
    execute_SUB,
)

MUL = register_instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) % 2**256)),
)
def div(ctx)->None:
    val = int(ctx.stack.pop() / ctx.stack.pop())
    val = val%2**256
    ctx.stack.push(val)
DIV = register_instruction(
    0x04,
    "DIV",
    div,
)

MSTORE8 = register_instruction(
    0x53,
    "MSTORE8",
    (lambda ctx: ctx.memory.store(ctx.stack.pop(),ctx.stack.pop()%2**256)),
)
MSTORE8 = register_instruction(
    0xf3,
    "RETURN",
    (lambda ctx: ctx.set_return_data(ctx.stack.pop(),ctx.stack.pop())),
)

JUMP = register_instruction(
    0x56,
    "JUMP",
  execute_JUMP,
)
JUMPI = register_instruction(
    0x57,
    "JUMPI",
  execute_JUMPI,
)

MSIZE = register_instruction(
    0x59,
    "MSIZE",
  lambda ctx: ctx.stack.push(32*ctx.memory.active_words()),
)


JUMPDEST = register_instruction(
    0x5b,
    "JUMPDEST",
  (lambda ctx: ctx),
)
PC = register_instruction(
    0x58,
    "PC",
  (lambda ctx: ctx.stack.push(ctx.pc)),
)

#PUSH INSTRUCTIONS
PUSH1 = register_instruction(0x60, "PUSH1", lambda ctx: ctx.stack.push(ctx.read_code(1)))
PUSH2 = register_instruction(0x61, "PUSH2", lambda ctx: ctx.stack.push(ctx.read_code(2)))
PUSH3 = register_instruction(0x62, "PUSH3", lambda ctx: ctx.stack.push(ctx.read_code(3)))
PUSH4 = register_instruction(0x63, "PUSH4", lambda ctx: ctx.stack.push(ctx.read_code(4)))
PUSH5 = register_instruction(0x64, "PUSH5", lambda ctx: ctx.stack.push(ctx.read_code(5)))
PUSH6 = register_instruction(0x65, "PUSH6", lambda ctx: ctx.stack.push(ctx.read_code(6)))
PUSH7 = register_instruction(0x66, "PUSH7", lambda ctx: ctx.stack.push(ctx.read_code(7)))
PUSH8 = register_instruction(0x67, "PUSH8", lambda ctx: ctx.stack.push(ctx.read_code(8)))
PUSH9 = register_instruction(0x68, "PUSH9", lambda ctx: ctx.stack.push(ctx.read_code(9)))
PUSH10 = register_instruction(0x69, "PUSH10", lambda ctx: ctx.stack.push(ctx.read_code(10)))
PUSH11 = register_instruction(0x6A, "PUSH11", lambda ctx: ctx.stack.push(ctx.read_code(11)))
PUSH12 = register_instruction(0x6B, "PUSH12", lambda ctx: ctx.stack.push(ctx.read_code(12)))
PUSH13 = register_instruction(0x6C, "PUSH13", lambda ctx: ctx.stack.push(ctx.read_code(13)))
PUSH14 = register_instruction(0x6D, "PUSH14", lambda ctx: ctx.stack.push(ctx.read_code(14)))
PUSH15 = register_instruction(0x6E, "PUSH15", lambda ctx: ctx.stack.push(ctx.read_code(15)))
PUSH16 = register_instruction(0x6F, "PUSH16", lambda ctx: ctx.stack.push(ctx.read_code(16)))
PUSH17 = register_instruction(0x70, "PUSH17", lambda ctx: ctx.stack.push(ctx.read_code(17)))
PUSH18 = register_instruction(0x71, "PUSH18", lambda ctx: ctx.stack.push(ctx.read_code(18)))
PUSH19 = register_instruction(0x72, "PUSH19", lambda ctx: ctx.stack.push(ctx.read_code(19)))
PUSH20 = register_instruction(0x73, "PUSH20", lambda ctx: ctx.stack.push(ctx.read_code(20)))
PUSH21 = register_instruction(0x74, "PUSH21", lambda ctx: ctx.stack.push(ctx.read_code(21)))
PUSH22 = register_instruction(0x75, "PUSH22", lambda ctx: ctx.stack.push(ctx.read_code(22)))
PUSH23 = register_instruction(0x76, "PUSH23", lambda ctx: ctx.stack.push(ctx.read_code(23)))
PUSH24 = register_instruction(0x77, "PUSH24", lambda ctx: ctx.stack.push(ctx.read_code(24)))
PUSH25 = register_instruction(0x78, "PUSH25", lambda ctx: ctx.stack.push(ctx.read_code(25)))
PUSH26 = register_instruction(0x79, "PUSH26", lambda ctx: ctx.stack.push(ctx.read_code(26)))
PUSH27 = register_instruction(0x7A, "PUSH27", lambda ctx: ctx.stack.push(ctx.read_code(27)))
PUSH28 = register_instruction(0x7B, "PUSH28", lambda ctx: ctx.stack.push(ctx.read_code(28)))
PUSH29 = register_instruction(0x7C, "PUSH29", lambda ctx: ctx.stack.push(ctx.read_code(29)))
PUSH30 = register_instruction(0x7D, "PUSH30", lambda ctx: ctx.stack.push(ctx.read_code(30)))
PUSH31 = register_instruction(0x7E, "PUSH31", lambda ctx: ctx.stack.push(ctx.read_code(31)))
PUSH32 = register_instruction(0x7F, "PUSH32", lambda ctx: ctx.stack.push(ctx.read_code(32)))

DUP1 = register_instruction(0x80, "DUP1", lambda ctx: ctx.stack.push(ctx.stack.peek(0)))
DUP2 = register_instruction(0x81, "DUP2", lambda ctx: ctx.stack.push(ctx.stack.peek(1)))
DUP3 = register_instruction(0x82, "DUP3", lambda ctx: ctx.stack.push(ctx.stack.peek(2)))
DUP4 = register_instruction(0x83, "DUP4", lambda ctx: ctx.stack.push(ctx.stack.peek(3)))
DUP5 = register_instruction(0x84, "DUP5", lambda ctx: ctx.stack.push(ctx.stack.peek(4)))
DUP6 = register_instruction(0x85, "DUP6", lambda ctx: ctx.stack.push(ctx.stack.peek(5)))
DUP7 = register_instruction(0x86, "DUP7", lambda ctx: ctx.stack.push(ctx.stack.peek(6)))
DUP8 = register_instruction(0x87, "DUP8", lambda ctx: ctx.stack.push(ctx.stack.peek(7)))
DUP9 = register_instruction(0x88, "DUP9", lambda ctx: ctx.stack.push(ctx.stack.peek(8)))
DUP10 = register_instruction(0x89, "DUP10", lambda ctx: ctx.stack.push(ctx.stack.peek(9)))
DUP11 = register_instruction(0x8A, "DUP11", lambda ctx: ctx.stack.push(ctx.stack.peek(10)))
DUP12 = register_instruction(0x8B, "DUP12", lambda ctx: ctx.stack.push(ctx.stack.peek(11)))
DUP13 = register_instruction(0x8C, "DUP13", lambda ctx: ctx.stack.push(ctx.stack.peek(12)))
DUP14 = register_instruction(0x8D, "DUP14", lambda ctx: ctx.stack.push(ctx.stack.peek(13)))
DUP15 = register_instruction(0x8E, "DUP15", lambda ctx: ctx.stack.push(ctx.stack.peek(14)))
DUP16 = register_instruction(0x8F, "DUP16", lambda ctx: ctx.stack.push(ctx.stack.peek(15)))

POP = register_instruction(0x50, "POP", lambda ctx: ctx.stack.pop())


SWAP1 = register_instruction(0x90, "SWAP1", lambda ctx: ctx.stack.swap(1))
def valid_jump_destinations(code: bytes) ->set[int]:
    jumpdests=set()
    i=0
    while i<len(code):
        current_op = code[i]
        if current_op == JUMPDEST.opcode:
            jumpdests.add(i)
        elif PUSH1.opcode <= current_op <= PUSH32.opcode:
            i+= current_op - PUSH1.opcode + 1
        i+=1
    return jumpdests

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


# thanks, https://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3
def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(max(1, (x.bit_length() + 7) // 8), "big")
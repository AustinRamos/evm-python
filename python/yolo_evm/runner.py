from .ExecutionContext import ExecutionContext
from .opcodes import decode_opcode


def run(code: bytes) -> ExecutionContext:
    """
    Executes code in a fresh context.
    """
    context = ExecutionContext(code=code)

    while not context.stopped:
        print("STACK CONTINUE: " , context.stack.stack)
        pc_before = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)
        print(f"{instruction.name} @ pc={pc_before}")
        print("stack: ", context.stack.stack)
        print("memory: " ,context.memory.memory)
        print()
    print(f"Output: 0x{context.returndata.hex()}")

    return context
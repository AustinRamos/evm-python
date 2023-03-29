from dataclasses import dataclass

from yolo_evm.ExecutionContext import ExecutionContext


@dataclass
class EVMException(Exception):
    context: ExecutionContext


class UnknownOpcode(EVMException):
    ...


class InvalidCodeOffset(EVMException):
    ...


@dataclass
class InvalidJumpDestination(EVMException):
    target_pc: int
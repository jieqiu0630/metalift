import re

from llvmlite.binding import ValueRef
from metalift.ir import And, Expr, Lit, BoolObject, IntObject, NewObject, Or, get_object_sources
from typing import Dict


def parseOperand(op: ValueRef, reg: Dict[str, NewObject], hasType: bool = True) -> NewObject:
    # op is a ValueRef, and if it has a name then it's a register
    if op.name:  # a reg
        try:
            return reg[op.name]
        except KeyError:
            # hack due to ValueRef only using referential equality
            for regKey in reg.keys():
                if str(regKey) == str(op):
                    return reg[regKey]
            raise KeyError("")
    elif hasType:  # i32 0
        val = re.search("\w+ (\S+)", str(op)).group(1)  # type: ignore
        if val == "true":
            return BoolObject(True)
        elif val == "false":
            return BoolObject(False)
        else:  # assuming it's a number
            return IntObject(int(val))
    else:  # 0
        return IntObject(int(op))


def and_exprs(*exprs: Expr) -> Expr:
    if len(exprs) == 1:
        return exprs[0]
    else:
        return And(*exprs)

def and_objects(*objects: BoolObject) -> BoolObject:
    return BoolObject(and_exprs(*get_object_sources(objects)))


# TODO: should this belong to the same function as and_exprs or different?
def or_exprs(*exprs: Expr) -> Expr:
    if len(exprs) == 1:
        return exprs[0]
    else:
        return Or(*exprs)

def or_objects(*objects: BoolObject) -> BoolObject:
    return BoolObject(or_exprs(*get_object_sources(objects)))

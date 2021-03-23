from parsec import *
import parsec
import operator

id_ = word()

namespace = {}

BINARY_OPS = {
    "+": operator.add,
    "-": operator.sub,
    "%": operator.mod,
    "*": operator.mul,
    "/": operator.truediv
}


def eval_binary(op, l, r):
    return BINARY_OPS[op](l, r)


def _group_part():
    return or_(add_expr(), mod_expr(), multiply_expr(), group_expr(), float_()).name("_group_part")


def group_expr():
    def p(state: State):
        lex("(")(state)
        r = _group_part()(state)
        lex(")")(state)
        return r
    return ParseC(p, "group_expr")


def _multiply_part():
    return or_(group_expr(), float_()).name("_multiply_part")


def multiply_expr():
    def p(state: State):
        l = _multiply_part()(state)
        op_parser = or_(lex("*"), lex("/"))
        while True:
            op = optional(op_parser)(state)
            if not op:
                break
            r = _multiply_part()(state)
            l = eval_binary(op, l, r)
        return l

    return ParseC(p, "multiply_expr")


def _mod_part():
    return or_(multiply_expr(), group_expr(), float_()).name("_mod_part")


def mod_expr():
    def p(state: State):
        l = _mod_part()(state)
        while True:
            op = optional(lex("%"))(state)
            if not op:
                break
            r = _mod_part()(state)
            l = eval_binary(op, l, r)
        return l

    return ParseC(p, "mod_expr")


def _add_part():
    return or_(mod_expr(), multiply_expr(), group_expr(), float_()).name("_add_part")


def add_expr():
    def p(state: State):
        l = _add_part()(state)
        op_parser = or_(lex("+"), lex("-"))
        while True:
            op = optional(op_parser)(state)
            if not op:
                break
            r = _add_part()(state)
            l = eval_binary(op, l, r)
        return l

    return ParseC(p, "add_exr")


def assign_expr():
    def p(state: State):
        _id = id_(state)
        lex("=")(state)
        value = add_expr()(state)
        namespace[_Id] = value
        return value

    return ParseC(p, "assign_expr")

def calc():
    return add_expr()

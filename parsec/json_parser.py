import operator
from parsec import *


def _const(result=None):
    def inner(*args, **kwargs):
        return result
    return inner


def json_parser():
    j_bool = or_(
        lex("true").map(_const(True)),
        lex("false").map(_const(False))).name("boolean")
    j_str = double_quoted_str().name("string")
    j_number = float_().name("number")

    def j_item():
        return or_(j_list(), j_object(), j_str, j_number, j_bool)

    def j_list():
        def p(state: State):
            lex("[")(state)
            r = optional(sepby(j_item(), lex(",")))(state)
            lex("]")(state)
            return r if r else []

        return ParseC(p, "JsonArray")

    def j_kv():
        def p(state: State):
            k = double_quoted_str()(state)
            lex(":")(state)
            v = j_item()(state)
            return (k, v)

        return ParseC(p, "JsonKVPair")

    def j_object():
        def p(state: State):
            lex("{")(state)
            r = optional(sepby(j_kv(), lex(",")))(state)
            lex("}")(state)
            return dict(r) if r else {}

        return ParseC(p, "JsonObject")

    return chain(optional(j_item()), eof()).map(operator.itemgetter(0))

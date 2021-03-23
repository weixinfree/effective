#! /usr/bin/env python3
from typing import Callable, Any, List, Iterable, Union
from functools import partial
import re


MISMATCH = object()


class State:
    index: int
    src: str
    size: int

    @staticmethod
    def of(s):
        if isinstance(s, State):
            return s
        assert isinstance(s, str)
        return State(s)

    def __init__(self, src):
        self.src = src
        self.size = len(src)
        self.index = 0

    def advance(self, step):
        self.index += step

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = self.index + (item.start or 0)
            stop = self.index + (item.stop or self.size)
            return self.src[start:stop:item.step]
        elif isinstance(item, int):
            return self.src[self.index + item]
        else:
            raise SystemExit("")


class ParseC:
    def __init__(self, f, name: str = None):
        self._name = name if name else f.__name__
        self._parse_func = f
        self._auto_skip_space = True

    def name(self, name: str):
        self._name = name
        return self

    def map(self, f):
        self._map_func = f
        return self

    def auto_skip_space(self, skip: bool = True):
        self._auto_skip_space = skip
        return self

    def skip(self, parser):
        self._skip_parser = parser
        return self

    def parse(self, s):
        s = State.of(s)
        r = self._parse_func(s)
        if r == MISMATCH:
            raise MismatchException(f'{self._name}', s)
        if hasattr(self, "_map_func"):
            r = self._map_func(r)
        if self._auto_skip_space:
            _regex_match(r"\s*", s)
        if hasattr(self, "_skip_parser"):
            self._skip_parser(s)
        return r

    def __call__(self, s):
        return self.parse(s)


class MismatchException(BaseException):
    def __init__(self, description: str, s: State):
        super().__init__(f'mismatch {description}, at: {s.index}')


def lex(chars: str):
    def p(state: State):
        if state[:len(chars)] == chars:
            state.advance(len(chars))
            return chars
        return MISMATCH
    return ParseC(p, f"lex({chars})")


def _regex_match(pat, state):
    m = re.match(pat, state[:])
    if m:
        start, stop = m.span()
        assert start == 0
        state.advance(stop)
        return m.group()
    return MISMATCH


def regex(pat: str, name: str = "regex"):
    p = partial(_regex_match, pat)
    return ParseC(p, name)


def eof():
    def p(state: State):
        return "EOF" if state.index == state.size else MISMATCH
    return ParseC(p, "eof")


def integer():
    return regex(r"[+-]?\d+", "integer").map(int)


def float_():
    return regex(r'[+-]?\d+(\.\d+)?', "float").map(float)


def alpha():
    return regex(r'[a-zA-Z]+', "alpha")


def word():
    return regex(r'\w+', "word")


def space():
    return regex(r'\s*', "space")


def single_quoted_str():
    return quoted_str(quote="'", name="single_quoted_str")


def double_quoted_str():
    return quoted_str(quote='"', name="double_quoted_str")


def tribble_quoted_str():
    return quoted_str(quote='```', name="tribble_quoted_str")


def quoted_str(quote: str = "'", name: str = "quoted_str"):
    def p(state: State):
        quote_len = len(quote)
        if state[:quote_len] != quote:
            return MISMATCH
        state.advance(quote_len)
        start = state.index
        while not (state[:quote_len] == quote and state[-1] != '\\'):
            state.advance(1)
        end = state.index
        state.advance(quote_len)
        return state.src[start: end]
    return ParseC(p, name)


################### combine #################

def _optional_match(parser, state: State):
    index = state.index
    try:
        return parser(state)
    except MismatchException as e:
        state.index = index
        return None


def sepby(body_parser, sep_parser):
    def p(state: State):
        r = []
        r.append(body_parser(state))
        while _optional_match(sep_parser, state):
            r.append(body_parser(state))
        return r
    return ParseC(p, "sepby")


def optional(parser):
    return ParseC(partial(_optional_match, parser), "optional")


def or_(*parsers):
    def p(state: State):
        index = state.index
        for p in parsers:
            try:
                return p(state)
            except MismatchException as e:
                state.index = index

        return MISMATCH

    return ParseC(p, f"or({', '.join(p._name for p in parsers)})")


def many1(parser):
    return many(parser, min_occur=1)


def many(parser, min_occur=0):
    def p(state: State):
        r = []
        for _ in range(min_occur):
            r.append(parser(state))
        while True:
            try:
                r.append(parser(state))
            except MismatchException as e:
                break
        return r
    return ParseC(p, f'many({min_occur})')


def chain(*parsers):
    def p(state: State):
        r = []
        for p in parsers:
            r.append(p(state))
        return r
    return ParseC(p, "chain")

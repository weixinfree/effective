from calc import *
import pytest

def verify(expr, parser):
    assert parser(expr) == eval(expr)

def test_add():
    verify("1 + 2", calc())
    verify("1 - 2", calc())
    verify("1 + 2 + 3", calc())
    verify("1+2-3", calc())
    assert calc()("1") == 1

def test_mod():
    verify("3 % 5", calc())
    verify("3 % 5 % 7", calc())


def test_mul():
    verify("3 * 5", calc())
    verify("3 / 5", calc())
    verify("1 * 2 * 3 / 6 / 7 * 8", calc())


def test_group():
    verify("(3 + 2)", calc())
    verify("3 + (5 % 2)", calc())
    with pytest.raises(MismatchException):
        verify("()", calc())

def test_complex_expr():
    pass
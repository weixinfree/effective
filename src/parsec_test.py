from parsec import *
import pytest


def assertEqual(left, right):
    assert left == right


def test_lex():
    s = State.of("hello world")
    assertEqual(lex("hello")(s), "hello")
    assertEqual(s.index, 6)
    assertEqual(lex("world")(s), "world")
    assertEqual(s.index, 11)


def test_lex_mismatch():
    with pytest.raises(MismatchException):
        lex("mismatch")("hello")


def test_regex():
    s = State.of("aaaa bbbb")
    assertEqual(regex(r"a{4}")(s), "aaaa")
    assertEqual(s.index, 5)
    assertEqual(regex(r'b+')(s), "bbbb")
    assertEqual(s.index, 9)


def test_integer():
    s = State.of("123abc")
    assertEqual(integer()(s), 123)
    assertEqual(s.index, 3)
    s2 = State.of("-123abc")
    assertEqual(integer()(s2), -123)
    assertEqual(s2.index, 4)


def test_float():
    s = State.of("123abc")
    assertEqual(float_()(s), 123.0)
    assertEqual(s.index, 3)
    s2 = State.of("123.456")
    assertEqual(float_()(s2), 123.456)
    assertEqual(s2.index, 7)
    s3 = State.of("-123.456")
    assertEqual(float_()(s3), -123.456)


def test_quoted_str():
    s = State.of('''"hello world"''')
    assertEqual(double_quoted_str()(s), "hello world")
    assertEqual(s.index, 13)

    s2 = State.of("""'hello world'""")
    assertEqual(single_quoted_str()(s2), "hello world")
    assertEqual(s2.index, 13)


def test_word():
    s = State.of("hello world-")
    assertEqual(word()(s), "hello")
    assertEqual(word()(s), "world")
    s2 = State.of("hello_world")
    assertEqual(word()(s2), "hello_world")


def test_alpha():
    s = State.of("abc")
    assert alpha()(s) == 'abc'


def test_eof():
    assert eof()("") == "EOF"
    s = State.of("demoabc")
    alpha()(s)
    assert eof()(s) == "EOF"


def test_skip_parser():
    p = lex("hello").skip(lex("world"))
    s = State.of("helloworld-h")
    assert p(s) == "hello"
    assert s.index == 10


def test_skip_space():
    s = State.of("hello world")
    lex("hello").auto_skip_space(False)(s)
    assert space()(s) == " "


def test_many():
    assert many(lex("1"))("111111") == ["1", "1", "1", "1", "1", "1"]
    assert many(lex("1"))("") == []
    assert many1(lex("1"))("111") == ["1", "1", "1"]

    with pytest.raises(MismatchException):
        many1(lex("1"))("")


def tes_or():
    parser = or_(lex("abc"), integer(), lex("def"))
    assert parser("abc") == "abc"
    assert parser("123") == 123
    assert parser("def") == "def"

    with pytest.raises(MismatchException):
        parser("()@")


def test_optional():
    parser = optional(integer())
    assert parser("123") == 123
    assert parser("abc") == None


def test_sepby():
    assert sepby(integer(), lex(","))("1,2,3,4,5abc") == [1, 2, 3, 4, 5]
    with pytest.raises(MismatchException):
        sepby(integer(), lex(","))("abc")


def test_chain():
    assert chain(lex("<"), word(), lex(">"))("<demo>") == ["<", "demo", ">"]

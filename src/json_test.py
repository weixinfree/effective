from json_parser import json_parser
import json


def test_json_unit():
    assert json_parser()("") == None
    assert json_parser()("1") == 1
    assert json_parser()("false") == False
    assert json_parser()("true") == True
    assert json_parser()("1.23") == 1.23
    assert json_parser()("{}") == {}
    assert json_parser()("[]") == []
    assert json_parser()('"hello world"') == "hello world"


def test_jsonobject():
    assert json_parser()('{"name": "hello"}') == {"name": "hello"}
    assert json_parser()('{}') == {}


def test_jsonarray():
    assert json_parser()('[]') == []
    assert json_parser()("[1,2,3]") == [1, 2, 3]
    assert json_parser()('["hello", 1.23, true, {}]') == ["hello", 1.23, True, {}]

def test_complex_json():
    with open("test_complex_json.json") as f:
        text = f.read()

    assert json.loads(text) == json_parser()(text)
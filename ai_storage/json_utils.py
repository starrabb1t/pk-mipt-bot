import json
import os


def json_dump(json_filepath, json_obj, indent=4):
    with open(json_filepath, 'w') as f:
        ser = json.dumps(json_obj, indent=indent)
        f.write(ser)


def json_load(json_filepath):
    assert_file(json_filepath)
    with open(json_filepath) as f:
        json_obj = json.load(f)
    return json_obj


def assert_file(filepath):
    errmsg = str(filepath) + ' should exists as file'
    assert os.path.isfile(filepath), errmsg

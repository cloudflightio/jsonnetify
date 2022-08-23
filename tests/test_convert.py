import json
from jsonnetify.jsonnetify import convert_manifest
import os


basedir = os.path.dirname(os.path.abspath(__file__))
manifest_jsonnet_path = os.path.join(basedir,"resources","manifest.libsonnet")
manifest_yaml_path = os.path.join(basedir,"resources","manifest.yaml")

def test_convert(capsys):
    convert_manifest( manifest_yaml_path, "-")
    captured = capsys.readouterr()
    result = json.loads("\n".join(str(captured.out).split("\n")[1:]))
    with open(manifest_jsonnet_path, "r") as f:
        expected = json.load(f)  
    assert result == expected

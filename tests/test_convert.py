import json
from tempfile import TemporaryDirectory
import threading
import http.server
from http.server import SimpleHTTPRequestHandler
from jsonnetify.jsonnetify import convert_manifest
import os
import sys


basedir = os.path.dirname(os.path.abspath(__file__))
manifest_jsonnet_path = os.path.join(basedir, "resources", "manifest.libsonnet")
manifest_yaml_path = os.path.join(basedir, "resources", "manifest.yaml")


def assert_manifest(o):
    result = json.loads("\n".join(o.split("\n")))
    with open(manifest_jsonnet_path, "r") as f:
        expected = json.load(f)
    assert result == expected


def test_convert_filein(capsys):
    convert_manifest(manifest_yaml_path, "-")
    captured = capsys.readouterr()
    assert_manifest(captured.out)


def test_convert_urlin(capsys):
    web_dir = os.path.join(os.path.dirname(__file__), "resources")
    os.chdir(web_dir)
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 6666), SimpleHTTPRequestHandler
    )
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    convert_manifest("http://127.0.0.1:6666/manifest.yaml", "-")
    captured = capsys.readouterr()
    assert_manifest(captured.out)


def test_convert_stdin(capsys):
    sys.stdin = open(manifest_yaml_path, "r")
    convert_manifest("-", "-")
    captured = capsys.readouterr()
    assert_manifest(captured.out)


def test_convert_fileout():
    tempdir = TemporaryDirectory()
    manifest_json_path = os.path.join(tempdir.name, "manifest.json")
    convert_manifest(manifest_yaml_path, manifest_json_path)
    with open(manifest_json_path, "r") as f:
        assert_manifest(f.read())

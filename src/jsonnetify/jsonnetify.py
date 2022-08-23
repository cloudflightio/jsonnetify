import argparse
import json
import sys
from typing import Optional, Tuple
from urllib import request
import yaml


def load_manifest(f):
    docs = yaml.safe_load_all(f)
    return {
        "-".join([doc["kind"], doc["metadata"]["name"]]).lower().replace(":", "-"): doc
        for doc in docs
    }


def convert_manifest(inputfile: str, outputfile: str, tempdir: Optional[str] = None):
    if inputfile.startswith(("http://", "https://")):
        (dl_file_path, _) = request.urlretrieve(inputfile)
        with open(dl_file_path, "r") as f:
            combined_manifest = load_manifest(f)
    elif inputfile == "-":
        combined_manifest = load_manifest(sys.stdin)
    else:
        with open(inputfile, "r") as f:
            combined_manifest = load_manifest(f)

    if outputfile == "-":
        json.dump(combined_manifest, sys.stdout, indent=4, sort_keys=True)
    else:
        with open(outputfile, "w") as f:
            json.dump(combined_manifest, f, indent=4, sort_keys=True)


def cli(argv=None) -> Tuple[str, str, Optional[str]]:
    parser = argparse.ArgumentParser(
        exit_on_error=True,
        prog="jsonnetify",
        description="Convert multi-doc kubernetes manifests into jsonnet",
    )
    parser.add_argument(
        "-i",
        "--ifile",
        help='Input (can be a url, path or "-" for stdin)',
        required=True,
        type=str,
    )
    parser.add_argument(
        "-o",
        "--ofile",
        help='Output (can be a path or "-" for stdout',
        required=True,
        type=str,
    )
    parser.add_argument(
        "-t", "--tmpdir", help="Temp directory path", required=False, type=str
    )
    args = vars(parser.parse_args(argv))

    outputfile = args["ofile"]
    inputfile = args["ifile"]
    tempdir = args.get("tmpdir", None)

    return (inputfile, outputfile, tempdir)


def main(argv=None):  # pragma: no cover
    if not argv:
        argv = sys.argv[1:]

    context = cli()
    convert_manifest(*context)

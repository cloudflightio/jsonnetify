import argparse
import sys
from typing import Any, Optional, TextIO, Tuple, Union
from urllib import request
import _jsonnet
import pathlib
from yaml2jsonnet.yaml2jsonnet import convert_yaml
from kubesplit.kubesplit import split_input_to_files
from kubesplit.config import KubesplitConfig, KubesplitIOConfig
from yamkix.config import get_default_yamkix_config
from tempfile import TemporaryDirectory
import os
import logging

def convert_manifest(
    inputfile: str, outputfile: str, tempdir : Optional[str] = None
):
    if not tempdir:
        tempdirobj = TemporaryDirectory("jsonnetify")
        tempdir = tempdirobj.name

    manifest_file_path = os.path.join(tempdir, "manifest.yaml")
    output_path = os.path.join(tempdir, "out")


    if inputfile.startswith(("http://", "https://")):
        request.urlretrieve(inputfile, manifest_file_path)
    elif inputfile == "-":
        with open(manifest_file_path, "w") as f:
            f.write(sys.stdin.read())
    else:
        with open(inputfile, "r") as fi:
            with open(manifest_file_path, "w") as fo:
                fo.write(fi.read())

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    ksConfig = KubesplitConfig(
        clean_output_dir=False,
        prefix_resource_files=False,
        version=False,
        io_config=KubesplitIOConfig(
            input=manifest_file_path,
            input_display_name="manifest.yaml",
            output_dir=output_path,
        ),
        yamkix_config=get_default_yamkix_config(),
    )
    split_input_to_files(ksConfig)

    for (path, _, files) in os.walk(output_path):
        for file in files:
            file_path_in = os.path.join(path, file)
            file_path_out = os.path.join(path, os.path.splitext(file)[0] + ".jsonnet")
            logging.info("processing " + file)
            with open(file_path_in, "r") as fi:
                with open(file_path_out, "w") as fo:
                    convert_yaml(fi.read(), fo, array=False, inject_comments=False)

    jsonnet_str = "{\n"
    for path in pathlib.Path(output_path).rglob("*.jsonnet"):
        key = os.path.splitext(os.path.basename(path))[0].replace("--", "-")
        file = str(path.absolute().resolve())
        jsonnet_str += f'  "{key}": import "{file}",\n'
    jsonnet_str += "}\n"

    json_str = _jsonnet.evaluate_snippet("snippet", jsonnet_str)

    if isinstance(outputfile, str):
        with open(outputfile, "w") as f:
            f.write(json_str)
    elif isinstance(outputfile, TextIO):
        outputfile.write(json_str)
    else:
        raise Exception("invalid outputfile!")


def cli(argv=None) -> Tuple[str,str,Optional[str]]:
    parser = argparse.ArgumentParser(exit_on_error=True, prog="jsonnetify", description='Convert multi-doc kubernetes manifests into jsonnet')
    parser.add_argument('-i','--ifile', help='Input (can be a url, path or "-" for stdin)', required=True, type=str)
    parser.add_argument('-o','--ofile', help='Output (can be a path or "-" for stdout', required=True, type=str)
    parser.add_argument('-t','--tmpdir', help='Temp directory path', required=False, type=str)
    args = vars(parser.parse_args(argv))

    outputfile = args['ofile']  
    inputfile = args['ifile']
    tempdir = args.get("tmpdir", None)

    return (inputfile, outputfile, tempdir)

def main(argv=None):
    if not argv:
        argv = sys.argv[1:]
    
    context = cli()
    convert_manifest(*context)

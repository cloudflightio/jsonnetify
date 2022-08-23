from jsonnetify.jsonnetify import cli
import pytest

def assert_help(result):
    assert "jsonnetify" in result
    assert "-i IFILE" in result
    assert "-o OFILE" in result
    assert "-t TMPDIR" in result

def assert_exit(pytest_wrapped_e):
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code > 0

def test_cli_no_args(capsys): 
    args = []
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli(args)
        assert_exit(pytest_wrapped_e)

    captured = capsys.readouterr()
    result = captured.err
    assert_help(result)

def test_cli_in_arg_missing(capsys): 
    args = ["-o","testout"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli(args)
        assert_exit(pytest_wrapped_e)

    captured = capsys.readouterr()
    result = captured.err
    assert_help(result)

def test_cli_out_arg_missing(capsys): 
    args = ["-i","testin"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli(args)
        assert_exit(pytest_wrapped_e)

    captured = capsys.readouterr()
    result = captured.err
    assert_help(result)

def test_cli_in_and_out_arg_missing(capsys): 
    args = ["-t","temp"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli(args)
        assert_exit(pytest_wrapped_e)

    captured = capsys.readouterr()
    result = captured.err
    assert_help(result)

def test_cli_valid_args_no_temp():
    args = ["-i", "testin", "-o", "testout"]
    (inputfile, outputfile, tempdir) = cli(args)
    assert inputfile == "testin"
    assert outputfile == "testout"
    assert tempdir == None

def test_cli_valid_args_with_temp():
    args = ["-i", "testin", "-o", "testout", "-t", "tempdir"]
    (inputfile, outputfile, tempdir) = cli(args)
    assert inputfile == "testin"
    assert outputfile == "testout"
    assert tempdir == "tempdir"

import databroker_optout


def test_version():
    assert hasattr(databroker_optout, "__version__")
    assert isinstance(databroker_optout.__version__, str)
    assert databroker_optout.__version__ == "0.1.0"

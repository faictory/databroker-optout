import broker_removal_kit


def test_version():
    assert hasattr(broker_removal_kit, "__version__")
    assert isinstance(broker_removal_kit.__version__, str)
    assert broker_removal_kit.__version__ == "0.1.0"

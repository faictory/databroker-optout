import pytest
import tempfile
import os
from broker_removal_kit.config import load_config
from broker_removal_kit.errors import BrokerKitError


class TestLoadConfigValid:
    def test_full_config_with_all_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('name = "Jordan Rivera"\n')
                f.write('email = "jordan@example.com"\n')
                f.write('address = "PO Box 1234, Portland, OR 97201"\n')
                f.write('deadnames = ["James Rivera"]\n')
                f.write('dir = "brk-out"\n')

            config = load_config(config_path)

            assert config['name'] == "Jordan Rivera"
            assert config['email'] == "jordan@example.com"
            assert config['address'] == "PO Box 1234, Portland, OR 97201"
            assert config['deadnames'] == ["James Rivera"]
            assert config['dir'] == "brk-out"

    def test_config_with_multiple_deadnames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('name = "Taylor Brown"\n')
                f.write('deadnames = ["Kim Brown", "Alex Brown"]\n')

            config = load_config(config_path)

            assert config['name'] == "Taylor Brown"
            assert config['deadnames'] == ["Kim Brown", "Alex Brown"]

    def test_config_with_only_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('name = "Jordan Rivera"\n')

            config = load_config(config_path)

            assert config['name'] == "Jordan Rivera"
            assert config['email'] is None
            assert config['address'] is None
            assert config['deadnames'] == []
            assert config['dir'] is None

    def test_config_with_only_deadnames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('deadnames = ["James Rivera"]\n')

            config = load_config(config_path)

            assert config['name'] is None
            assert config['email'] is None
            assert config['address'] is None
            assert config['deadnames'] == ["James Rivera"]
            assert config['dir'] is None

    def test_empty_config_all_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('')

            config = load_config(config_path)

            assert config['name'] is None
            assert config['email'] is None
            assert config['address'] is None
            assert config['deadnames'] == []
            assert config['dir'] is None

    def test_config_missing_optional_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('name = "Alex Smith"\n')
                f.write('email = "alex@example.com"\n')

            config = load_config(config_path)

            assert config['name'] == "Alex Smith"
            assert config['email'] == "alex@example.com"
            assert config['address'] is None
            assert config['deadnames'] == []
            assert config['dir'] is None


class TestLoadConfigErrors:
    def test_nonexistent_file_raises_brokerkiterror(self):
        with pytest.raises(BrokerKitError) as exc_info:
            load_config("/nonexistent/path/config.toml")

        assert "config file not found" in str(exc_info.value)

    def test_malformed_toml_raises_brokerkiterror(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('name = "Jordan Rivera"\n')
                f.write('invalid toml syntax here ]\n')

            with pytest.raises(BrokerKitError) as exc_info:
                load_config(config_path)

            assert "invalid TOML" in str(exc_info.value)

    def test_unclosed_string_raises_brokerkiterror(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('name = "Jordan Rivera\n')

            with pytest.raises(BrokerKitError) as exc_info:
                load_config(config_path)

            assert "invalid TOML" in str(exc_info.value)

    def test_invalid_array_syntax_raises_brokerkiterror(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.toml")
            with open(config_path, 'w') as f:
                f.write('deadnames = ["James", "Kim"\n')

            with pytest.raises(BrokerKitError) as exc_info:
                load_config(config_path)

            assert "invalid TOML" in str(exc_info.value)

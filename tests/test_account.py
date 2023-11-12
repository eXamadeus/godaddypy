from os import path, environ
from pathlib import Path
from unittest.mock import mock_open, patch, call

from godaddypy import Account


class TestAccount(object):
    mocked_file = mock_open(
        read_data="""
                    key: FILE_KEY
                    secret: FILE_SEC
                """
    )

    def test_account_config_from_constructor(self):
        headers = Account("FAKE_KEY", "FAKE_SECRET").get_headers()
        assert headers == {"Authorization": "sso-key FAKE_KEY:FAKE_SECRET"}

    def test_configure_via_env(self):
        with patch("os.environ", {"GODADDY_API_KEY": "ENV_KEY", "GODADDY_API_SECRET": "ENV_SEC"}):
            # make sure we mock a file here, to ensure it's ignored when env vars are set
            with patch("godaddypy.account.open", self.mocked_file):
                headers = Account().get_headers()

        assert headers == {"Authorization": "sso-key ENV_KEY:ENV_SEC"}

    def test_configure_override_env(self):
        with patch("os.environ", {"GODADDY_API_KEY": "ENV_KEY", "GODADDY_API_SECRET": "ENV_SEC"}):
            headers = Account(api_key="OVERRIDE_KEY", api_secret="OVERRIDE_SECRET").get_headers()

        assert headers == {"Authorization": "sso-key OVERRIDE_KEY:OVERRIDE_SECRET"}

    def test_account_config_via_file(self):
        with patch("godaddypy.account.open", self.mocked_file):
            headers = Account().get_headers()

        assert headers == {"Authorization": "sso-key FILE_KEY:FILE_SEC"}

    def test_configure_via_cli(self):
        file = mock_open()
        with patch("godaddypy.account.open", file) as m:
            with patch("builtins.input", side_effect=["FAKE_KEY", "FAKE_SECRET"]):
                with patch("yaml.dump") as dump:
                    Account.configure()

        m.assert_called_with(
            Path(path.expanduser(environ.get("XDG_CONFIG_HOME", "~/.config"))) / "godaddypy" / "credentials.yaml",
            mode="w",
        )

        assert dump.call_args.args[0] == {"key": "FAKE_KEY", "secret": "FAKE_SECRET"}

    def test_account_config_from_file_with_existing_file(self):
        self.mocked_file.reset_mock()
        with patch("godaddypy.account.open", self.mocked_file) as m:
            with patch("sys.stdout.write") as fake_out:
                with patch("builtins.input", side_effect=["FAKE_KEY_INPUT", "FAKE_SECRET_INPUT"]):
                    with patch("yaml.dump") as dump:
                        Account.configure()

        m.assert_called_with(
            Path(path.expanduser(environ.get("XDG_CONFIG_HOME", "~/.config"))) / "godaddypy" / "credentials.yaml",
            mode="w",
        )

        fake_out.assert_has_calls(
            [
                call("Enter GoDaddy API Key [****************_KEY]: "),
                call("Enter GoDaddy API Secret [****************_SEC]: "),
            ]
        )

        assert dump.call_args.args[0] == {"key": "FAKE_KEY_INPUT", "secret": "FAKE_SECRET_INPUT"}

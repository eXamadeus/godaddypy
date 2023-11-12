from os import path, environ
from pathlib import Path
from unittest.mock import mock_open, patch, call

from godaddypy import Account


class TestAccount(object):
    def test_account_config_from_constructor(self):
        headers = Account("FAKE_KEY", "FAKE_SECRET").get_headers()
        assert headers == {"Authorization": "sso-key FAKE_KEY:FAKE_SECRET"}

    def test_account_config_from_file(self):
        with patch(
            "godaddypy.account.open",
            mock_open(
                read_data="""
                    key: FAKE_KEY_FROM_FILE
                    secret: FAKE_SECRET_FROM_FILE
                """
            ),
        ) as m:
            headers = Account().get_headers()

        assert headers == {"Authorization": "sso-key FAKE_KEY_FROM_FILE:FAKE_SECRET_FROM_FILE"}
        # This is somewhat superfluous, but it's nice to know that the correct file was opened
        m.assert_called_once_with(
            Path(path.expanduser(environ.get("XDG_CONFIG_HOME", "~/.config"))) / "godaddypy" / "credentials.yaml",
            mode="r",
        )

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
        with patch(
            "godaddypy.account.open",
            mock_open(
                read_data="""
                        key: FAKE_KEY
                        secret: FAKE_SEC
                    """
            ),
        ) as m:
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

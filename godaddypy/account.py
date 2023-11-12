__all__ = ["Account"]

import logging
from dataclasses import dataclass
from os import environ, path, makedirs
from pathlib import Path
from sys import stdout

import yaml
from configloader import ConfigLoader


@dataclass
class Configuration:
    key: str = ""
    secret: str = ""


class InteractivePrompter:
    __masked_fields: set = {
        "GODADDY_API_KEY",
        "GODADDY_API_SECRET",
    }

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def mask_value(current_value):
        if current_value is None:
            return "None"
        else:
            return ("*" * 16) + current_value[-4:]

    @staticmethod
    def input(prompt):
        stdout.write(prompt)
        stdout.flush()
        return input()

    def get_value(self, current_value, config_name, prompt_text=""):
        if config_name in self.__masked_fields:
            current_value = "None" if not current_value else self.mask_value(current_value)
        response = self.input("%s [%s]: " % (prompt_text, current_value))
        if not response:
            response = None
        return response


class Account(object):
    """The GoDaddyPy Account.

    An account is used to provide authentication headers to the `godaddypy.Client`.
    """

    _SSO_KEY_TEMPLATE = "sso-key {api_key}:{api_secret}"

    __api_key = None
    __api_secret = None

    _logger = logging.getLogger("GoDaddyPy.Account")
    _log_level = logging.ERROR
    _config_path = Path(
        path.expanduser(environ.get("XDG_CONFIG_HOME", "~/.config")),
        "godaddypy/credentials.yaml",
    )
    _config = None

    def __init__(self, api_key=None, api_secret=None, delegate=None, log_level=None):
        """Create a new `godaddypy.Account` object.

        :type api_key: str or unicode
        :param api_key: The API_KEY provided by GoDaddy

        :type api_secret: str or unicode
        :param api_secret: The API_SECRET provided by GoDaddy
        """

        if log_level is not None:
            self._logger.setLevel(log_level)
        else:
            self._logger.setLevel(self._log_level)

        self._delegate = delegate

        if api_key:
            self.__api_key = api_key
        if api_secret:
            self.__api_secret = api_secret

        if self.__api_key and self.__api_secret:
            return  # prefer the passed values

        config = self.__parse_configuration()

        if not config:
            raise ValueError("Please use Account.configure() or pass api_key and api_secret to Account()")

        self.__api_key = self.__api_key or (config.key if config else api_key)
        self.__api_secret = self.__api_secret or (config.secret if config else api_secret)
        self._config = config

    def __parse_configuration(self) -> Configuration | None:
        # Get config from environment
        env_config = self.__parse_env()

        if env_config and env_config.key and env_config.secret:
            return env_config

        # Otherwise, get config from file according to XDG Base Directory Specifications
        # See: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
        return self.__parse_file()

    def __parse_file(self) -> Configuration | None:
        if not self or not path.exists(self._config_path):
            return None

        config = ConfigLoader()

        try:
            with open(self._config_path, mode="r") as config_file:
                config.update_from_yaml_file(config_file)
        except FileNotFoundError:
            self._logger.debug("Unable to find credentials file. Trying environment...")
            return None
        except (TypeError, Exception):
            self._logger.error("Error while loading credentials file. File will be overwritten.")
            return None

        key, secret = config.get("key"), config.get("secret")

        return Configuration(key=key, secret=secret)

    def __parse_env(self) -> Configuration | None:
        config = ConfigLoader()
        config.update_from_env_namespace("GODADDY_API")

        try:
            return Configuration(key=config["KEY"], secret=config["SECRET"])
        except KeyError:
            self._logger.debug("Unable to find credentials in environment.")
            return None

    def get_headers(self):
        headers = {
            "Authorization": self._SSO_KEY_TEMPLATE.format(
                api_key=self.__api_key,
                api_secret=self.__api_secret,
            )
        }

        if self._delegate is not None:
            headers["X-Shopper-Id"] = self._delegate

        return headers

    def configure_shell(self):
        config = self._config if self._config else self.__parse_configuration()
        prompter = InteractivePrompter()

        key = prompter.get_value(getattr(config, "key", None), "GODADDY_API_KEY", "Enter GoDaddy API Key")
        secret = prompter.get_value(getattr(config, "secret", None), "GODADDY_API_KEY", "Enter GoDaddy API Secret")

        parent = self._config_path.parent
        if not path.exists(parent):
            makedirs(parent)

        with open(self._config_path, mode="w") as config_file:
            yaml.dump({"key": key or config.key, "secret": secret or config.secret}, config_file)

    @staticmethod
    def configure():
        Account(api_key="api", api_secret="secret").configure_shell()

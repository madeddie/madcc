import os
import sys
from imp import load_source
from pathlib import Path
from . import const


class Settings(dict):
    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value

    def init(self, args=None):
        """Fills `settings` with values from `settings.py` and env."""
        self._setup_user_dir()
        self._init_settings_file()

        try:
            self.update(self._settings_from_file())
        except Exception:
            exception("Can't load settings from file", sys.exc_info())

        # try:
        #     self.update(self._settings_from_env())
        # except Exception:
        #     exception("Can't load settings from env", sys.exc_info())

        # self.update(self._settings_from_args(args))

    def _setup_user_dir(self):
        """Returns user config dir, create it when it doesn't exist."""
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME', '~/.config')
        user_dir = Path(xdg_config_home, 'madcc').expanduser()

        if not user_dir.is_dir():
            user_dir.mkdir(parents=True)
        self.user_dir = user_dir

    def _init_settings_file(self):
        """Create default settings file if it does not exist."""
        settings_path = self.user_dir.joinpath('settings.py')
        if not settings_path.is_file():
            with settings_path.open(mode='w') as settings_file:
                settings_file.write(const.SETTINGS_HEADER)
                for setting in const.DEFAULT_SETTINGS.items():
                    settings_file.write(u'# {} = {}\n'.format(*setting))

    def _settings_from_file(self):
        """Loads settings from file."""
        settings = load_source(
            'settings', str(self.user_dir.joinpath('settings.py')))
        return {key: getattr(settings, key)
                for key in const.DEFAULT_SETTINGS.keys()
                if hasattr(settings, key)}


settings = Settings(const.DEFAULT_SETTINGS)

import os
import dataclasses
import json
import traceback

from stfed.model.user_preferences import UserPreferences
from stfed.state import Publisher


class UserPreferencesRepo:
    def __init__(self):
        self.__path = os.path.expanduser(os.path.join('~', '.stfed.conf'))
        self.__modified = False
        self.__publisher = Publisher[UserPreferences]()
        self.__publisher.next(self.__load())

    def is_setup(self) -> bool:
        return os.path.exists(self.__path)

    def values(self) -> Publisher[UserPreferences]:
        return self.__publisher

    def get(self) -> UserPreferences:
        return self.__publisher.snapshot()

    def update(self, prefs: UserPreferences) -> None:
        self.__modified = True
        self.__publisher.next(prefs)

    def __load(self) -> UserPreferences:
        defaults = UserPreferences([], [], True, False)
        if not self.is_setup():
            return defaults
        try:
            with open(self.__path, 'r') as f:
                raw_json = json.load(f)
            result = UserPreferences(**raw_json)
            return result
        except:
            traceback.print_exc()
            return defaults

    def commit(self):
        if not self.__modified:
            return
        with open(self.__path, 'w') as f:
            json.dump(dataclasses.asdict(self.__publisher.snapshot()), f, indent=4)
            

repo = UserPreferencesRepo()

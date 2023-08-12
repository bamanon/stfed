import os
import dataclasses
import json
import traceback

import reactivex

from stfed.model.user_preferences import UserPreferences


class UserPreferencesRepo:
    def __init__(self):
        self.__path = os.path.expanduser(os.path.join('~', '.stfed.conf'))
        self.__modified = False
        self.__snapshot = self.__load()
        self.__subject = reactivex.subject.BehaviorSubject(self.__snapshot)

    def is_setup(self) -> bool:
        return os.path.exists(self.__path)

    def values(self) -> reactivex.Observable[UserPreferences]:
        return self.__subject

    def get(self) -> UserPreferences:
        return self.__snapshot

    def update(self, prefs: UserPreferences) -> None:
        self.__modified = True
        self.__snapshot = prefs
        self.__subject.on_next(prefs)

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
            json.dump(dataclasses.asdict(self.__snapshot), f, indent=4)
            

repo = UserPreferencesRepo()

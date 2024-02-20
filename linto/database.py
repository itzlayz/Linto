# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

from lightdb import LightDB
from typing import KT, VT


class Database(LightDB):
    def __init__(self, location: str) -> None:
        super().__init__(location)

    def __repr__(self):
        return object.__repr__(self)

    def set(self, name: str, key: KT, value: VT):
        self.setdefault(name, {})[key] = value
        return self.save()

    def get(self, name: str, key: KT, default: VT = None):
        try:
            return self[name][key]
        except KeyError:
            return default

    def pop(self, name: str, key: KT = None, default: VT = None):
        if not key:
            value = self.pop(name, default)
        else:
            try:
                value = self[name].pop(key, default)
            except KeyError:
                value = default

        self.save()
        return value

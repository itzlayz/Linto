# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import typing
from abc import abstractmethod

from utils import strtobool

ALLOWED_TYPES = [int, float, str, bool]


class Validator:
    def __init__(self, value: typing.Any):
        self.value = value

    @staticmethod
    @abstractmethod
    def validate(value: typing.Any) -> None:
        pass


class Integer(Validator):
    def __init__(self, value: int, *, _min: int = None, _max: int = None):
        self.validate(value, _min=_min, _max=_max)
        self.range = (_min, _max)

        super().__init__(value)

    @staticmethod
    def validate(value: int, *, _min: int = None, _max: int = None) -> None:
        if not isinstance(value, int):
            raise ValueError("Value must be an integer")

        if _min is not None and value < _min:
            raise ValueError("Value cannot be less than the minimum value")
        if _max is not None and value > _max:
            raise ValueError("Value cannot be greater than the maximum value")


class Float(Validator):
    def __init__(
        self,
        value: float,
        *,
        _min: typing.Union[float, int] = None,
        _max: typing.Union[float, int] = None
    ):
        self.validate(value, _min=_min, _max=_max)
        self.range = (_min, _max)

        super().__init__(value)

    @staticmethod
    def validate(value: float, *, _min: float = None, _max: float = None) -> None:
        if not isinstance(value, float):
            raise ValueError("Value must be a float")

        if _min is not None and value < _min:
            raise ValueError("Value cannot be less than the minimum value")
        if _max is not None and value > _max:
            raise ValueError("Value cannot be greater than the maximum value")


class String(Validator):
    def __init__(self, value: str, *, min_len: int = None, max_len: int = None):
        self.validate(value, min_len=min_len, max_len=max_len)
        self.range = (min_len, max_len)

        super().__init__(value)

    @staticmethod
    def validate(value: str, *, min_len: int = None, max_len: int = None) -> None:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        if min_len is not None and value < min_len:
            raise ValueError("Value cannot be less than the minimum value")
        if max_len is not None and value > max_len:
            raise ValueError("Value cannot be greater than the maximum value")


class Bool(Validator):
    def __init__(self, value: bool):
        super().__init__(value)

    @staticmethod
    def validate(value: bool):
        if not isinstance(value, bool):
            try:
                strtobool(value)
            except ValueError:
                raise ValueError("Value must be a bool")

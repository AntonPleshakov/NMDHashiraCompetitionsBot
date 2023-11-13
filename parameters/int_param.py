from config.config import getconf
from parameters import Param


class IntParam(Param):
    def __init__(self, name: str, view: str):
        super().__init__(name, view)
        self.value: int = int(getconf(self.name))

    def data_regexp_repr(self):
        return "\d+"

    def __int__(self):
        return self.value

    def data(self) -> str:
        return str(self.value)

    def value_repr(self) -> str:
        return str(self.value)

    def set_value(self, value: str):
        self.value = int(value)

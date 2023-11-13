from config.config import getconf
from parameters import Param


class BoolParam(Param):
    def __init__(self, name: str, view: str):
        super().__init__(name, view)
        self.value: bool = getconf(self.name) == "true"

    def data_regexp_repr(self):
        return "\w+"

    def __bool__(self):
        return self.value

    def data(self) -> str:
        return str("1" if self.value else "0")

    def value_repr(self) -> str:
        return "Включено" if self.value else "Отключено"

    def set_value(self, value: str):
        from_data = value == "1"
        from_repr = value == "Включено"
        from_str = value == "True"
        from_conf = value == "true"
        self.value = from_data or from_repr or from_str or from_conf

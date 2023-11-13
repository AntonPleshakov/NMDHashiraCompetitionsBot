from abc import ABC, abstractmethod
from typing import Dict


class Param(ABC):
    def __init__(self, name: str, view: str):
        self.name: str = name
        self.view: str = view

    @abstractmethod
    def data_regexp_repr(self) -> str:
        pass

    @abstractmethod
    def data(self) -> str:
        pass

    @abstractmethod
    def value_repr(self) -> str:
        pass

    @abstractmethod
    def set_value(self, value: str):
        pass


class Parameters:
    def params(self) -> Dict[str, Param]:
        result = {}
        for name, value in vars(self).items():
            if isinstance(value, Param):
                result[name] = value
        return result

    def to_data(self):
        return "/".join([v.data() for v in self.params().values()])

    @classmethod
    def from_data(cls, data: str):
        settings = cls()
        values = data.split("/")
        for attr, value in zip(settings.params(), values):
            settings.set_value(attr, value)
        return settings

    def data_regexp_repr(self):
        result = ""
        for param in self.params().values():
            if len(result) > 0:
                result += "/"
            result += param.data_regexp_repr()

        return result

    def view(self):
        text = ""
        for param in self.params().values():
            text += f"{param.view}: {param.value_repr()}\n"
        return text

    def set_value(self, attr_name: str, value: any):
        if isinstance(value, str):
            getattr(self, attr_name).set_value(value)
        else:
            getattr(self, attr_name).value = value

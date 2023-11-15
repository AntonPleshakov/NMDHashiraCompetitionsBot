from abc import ABC, abstractmethod
from typing import Dict

from db.gapi.worksheet_manager import Matrix


class Param(ABC):
    def __init__(self, name: str, view: str):
        self.name: str = name
        self.view: str = view

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

    def to_matrix(self) -> Matrix:
        result: Matrix = []
        for param in self.params().values():
            result.append([param.view, param.value_repr()])
        return result

    @classmethod
    def from_matrix(cls, matrix: Matrix):
        settings = cls()
        for attr, row in zip(settings.params(), matrix):
            settings.set_value(attr, row[1])
        return settings

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

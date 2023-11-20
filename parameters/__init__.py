from abc import ABC, abstractmethod
from typing import Dict, List

from db.gapi.worksheet_manager import Matrix


class Param(ABC):
    def __init__(self, view: str):
        self.view: str = view

    def value_repr(self) -> str:
        pass

    def __str__(self):
        return self.value_repr()

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

    def __eq__(self, other):
        for param in self.params():
            if getattr(self, param) != getattr(other, param):
                return False
        return True

    def to_matrix(self) -> Matrix:
        result: Matrix = []
        for param in self.params().values():
            result.append([param.view, param.value_repr()])
        return result

    @classmethod
    def from_matrix(cls, matrix: Matrix):
        parameters = cls()
        for attr, row in zip(parameters.params(), matrix):
            parameters.set_value(attr, row[1])
        return parameters

    def to_row(self) -> List[str]:
        return [param.value_repr() for param in self.params().values()]

    @classmethod
    def from_row(cls, row: List[str]):
        parameters = cls()
        for attr, value in zip(parameters.params(), row):
            parameters.set_value(attr, value)
        return parameters

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

from parameters import Parameters
from parameters.int_param import IntParam
from parameters.str_param import StrParam


class RegistrationRow(Parameters):
    def __init__(self):
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.tg_id: IntParam = IntParam("ТГ ID")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: IntParam = IntParam("Рейтинг")


class Match(Parameters):
    def __init__(self):
        self.first: StrParam = StrParam("Первый игрок")
        self.result: StrParam = StrParam("Результат")
        self.second: StrParam = StrParam("Второй игрок")
        self.map: StrParam = StrParam("Карта")
        self.battleground_effect: StrParam = StrParam("Эффект поля")


class Result(Parameters):
    def __init__(self):
        self.place: IntParam = IntParam("Место")
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: IntParam = IntParam("Рейтинг")
        self.mm: IntParam = IntParam("Очки")
        self.sos: IntParam = IntParam("SOS")
        self.sodos: IntParam = IntParam("SODOS")

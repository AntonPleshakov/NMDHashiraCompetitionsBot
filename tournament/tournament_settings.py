import datetime

from config.config import getconf
from parameters import Parameters
from parameters.bool_param import BoolParam
from parameters.int_param import IntParam


class TournamentSettings(Parameters):
    def __init__(self):
        self.rounds_number: IntParam = IntParam("Количество раундов")
        self.registration_duration_hours: IntParam = IntParam("Длительность регистрации в часах")
        self.round_duration_hours: IntParam = IntParam("Длительность раунда в часах")
        self.nightmare_matches: IntParam = IntParam("Количество Nightmare матчей")
        self.dangerous_matches: IntParam = IntParam("Количество Dangerous матчей")
        self.element_effect_map: BoolParam = BoolParam("Элементные слабости на поле")

    @property
    def round_duration_seconds(self) -> int:
        return datetime.timedelta(hours=self.round_duration_hours.value).seconds

    def registration_duration_seconds(self) -> int:
        return datetime.timedelta(hours=self.registration_duration_hours.value).seconds

    @classmethod
    def default_settings(cls):
        settings = cls()
        for name, param in settings.params().items():
            param.set_value(getconf(name))
        return settings

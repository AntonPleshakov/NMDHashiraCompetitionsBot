import datetime

from parameters import Parameters
from parameters.bool_param import BoolParam
from parameters.int_param import IntParam


class TournamentSettings(Parameters):
    def __init__(self):
        self.rounds_number: IntParam = IntParam("ROUNDS_NUMBER", "Количество раундов")
        self.round_duration_hours: IntParam = IntParam(
            "ROUND_DURATION_HOURS", "Длительность раунда в часах"
        )
        self.nightmare_matches: IntParam = IntParam(
            "NIGHTMARE_MATCHES", "Количество Nightmare матчей"
        )
        self.dangerous_matches: IntParam = IntParam(
            "DANGEROUS_MATCHES", "Количество Dangerous матчей"
        )
        self.element_effect_map: BoolParam = BoolParam(
            "ELEMENT_EFFECT_MAP", "Элементные слабости на поле"
        )

    @property
    def round_duration_seconds(self) -> int:
        return datetime.timedelta(hours=self.round_duration_hours.value).seconds

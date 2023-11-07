import datetime

from config.config import getconf


class TournamentSettings:
    rounds_number: int = 5
    round_duration_hours: int = 24
    nightmare_matches: int = 0
    dangerous_matches: int = 2
    element_effect_map_disabled: bool = True

    def round_duration_seconds(self) -> int:
        return datetime.timedelta(hours=self.round_duration_hours).seconds

    def to_data(self):
        return f"{self.rounds_number}/{self.round_duration_hours}/{self.nightmare_matches}/{self.dangerous_matches}/{self.element_effect_map_disabled}"

    @classmethod
    def from_data(cls, data: str):
        values = data.split("/")
        settings = cls()
        settings.rounds_number = int(values[0])
        settings.round_duration_hours = int(values[1])
        settings.nightmare_matches = int(values[2])
        settings.dangerous_matches = int(values[3])
        settings.element_effect_map_disabled = values[4] == "True"

    @staticmethod
    def data_regexp_repr():
        return "\d+/\d+/\d+/\d+/\w+"

    def __str__(self):
        element_effect_str = (
            "Отключены" if self.element_effect_map_disabled else "Включены"
        )
        text = (
            f"Количество раундов: {self.rounds_number}"
            + f"Длительность раунда в часах: {self.round_duration_hours}"
            + f"Количество Nightmare матчей: {self.nightmare_matches}"
            + f"Количество Dangerous матчей: {self.dangerous_matches}"
            + f"Элементные слабости на поле: {element_effect_str}"
        )
        return text

    @classmethod
    def get_default_tournament_settings(cls):
        settings = cls()
        settings.rounds_number = getconf("ROUNDS_NUMBER")
        settings.round_duration_hours = getconf("ROUND_DURATION_HOURS")
        settings.nightmare_matches = getconf("NIGHTMARE_MATCHES")
        settings.dangerous_matches = getconf("DANGEROUS_MATCHES")
        settings.element_effect_map_disabled = getconf("ELEMENT_EFFECT_MAP_DISABLED")
        return settings

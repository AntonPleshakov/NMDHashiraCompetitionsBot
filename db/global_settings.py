from config.config import getconf
from logger.NMDLogger import nmd_logger
from parameters import Parameters
from parameters.bool_param import BoolParam
from parameters.int_param import IntParam
from .gapi.gsheets_manager import GSheetsManager
from .gapi.worksheet_manager import WorksheetManager


class GlobalSettings(Parameters):
    def __init__(self):
        self.auto_tournament_enabled: BoolParam = BoolParam(
            "Автоматический запуск турниров"
        )
        self.tournaments_days_period: IntParam = IntParam(
            "Периодичность турниров в днях"
        )
        self.tournament_start_time_hours: IntParam = IntParam(
            "Время начала турнира по Москве (часы)"
        )
        self.tournament_start_time_minutes: IntParam = IntParam(
            "Время начала турнира по Москве (минуты)"
        )
        # default settings
        self.rounds_number: IntParam = IntParam("Количество раундов")
        self.registration_duration_hours: IntParam = IntParam(
            "Длительность регистрации в часах"
        )
        self.round_duration_hours: IntParam = IntParam("Длительность раунда в часах")
        self.nightmare_matches: IntParam = IntParam("Количество Nightmare матчей")
        self.dangerous_matches: IntParam = IntParam("Количество Dangerous матчей")
        self.element_effect_map: BoolParam = BoolParam("Элементные слабости на поле")


class SettingsDB:
    def __init__(self):
        ss_name = getconf("ADMINS_GTABLE_KEY")
        ws_name = getconf("ADMINS_SETTINGS_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )
        self._settings: GlobalSettings = GlobalSettings.from_matrix(
            self._manager.get_all_values()
        )

    @property
    def settings(self) -> GlobalSettings:
        return self._settings

    @settings.setter
    def settings(self, value: GlobalSettings):
        nmd_logger.info(f"DB: new global settings: {value.to_matrix()}")
        self._settings = value
        self._manager.update_values(value.to_matrix())


settings_db = SettingsDB()

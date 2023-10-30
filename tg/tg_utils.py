import telebot


BTN_TEXT = {
    "admins_button": "Администраторы",
    "add_admin": "Добавить администратора",
    "ratings_button": "Рейтинги",
    "add_rating": "Добавить рейтинг",
    "tournament_button": "Турнир",
    "dev_button": "Служебное",
    "upload_logs": "Загрузить логи",
    "update_config": "Обновить файл конфигурации",
    "home_button": "В начало",
}


def button(btn_data: str, path: str = ""):
    if path:
        callback_data = path + "/" + btn_data
    else:
        callback_data = btn_data
    return telebot.types.InlineKeyboardButton(
        text=BTN_TEXT[btn_data], callback_data=callback_data
    )


HOME_BTN = button("home_button")

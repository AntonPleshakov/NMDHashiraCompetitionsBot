from db.ratings import Rating
from db.tournament_structures import RegistrationRow, TournamentSettings

TEST_DATA_ADMINS = [
    ("Anton", 1),
    ("Ivan", 2),
    ("Max", 3),
    ("Sam", 4),
    ("Nikita", 5),
    ("Sergey", 6),
    ("Kirill", 7),
    ("Georgiy", 8),
]

# Each next user should be placed first after sort by rating
TEST_DATA_PLAYERS = [
    Rating.from_row(["Anton", 123, "NMD_Anton", 100, 100]),
    Rating.from_row(["Ivan", 123, "NMD_Ivan", 200, 100]),
    Rating.from_row(["Max", 123, "NMD_Max", 300, 100]),
    Rating.from_row(["Sam", 123, "NMD_Sam", 400, 100]),
    Rating.from_row(["Nikita", 123, "NMD_Nikita", 500, 100]),
    Rating.from_row(["Sergey", 123, "NMD_Sergey", 600, 100]),
    Rating.from_row(["Kirill", 123, "NMD_Kirill", 700, 100]),
    Rating.from_row(["Georgiy", 123, "NMD_Georgiy", 800, 100]),
]


DEFAULT_TOURNAMENT_SETTINGS = TournamentSettings.from_row([1, 1, 1, 1, "True"])


def ratingToRegistration(player: Rating):
    return RegistrationRow.from_row(player.to_row()[:-1])

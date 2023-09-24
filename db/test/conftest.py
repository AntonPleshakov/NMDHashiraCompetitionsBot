from tournament.player import Player


TEST_DATA_ADMINS = [
    ("Anton", "1"),
    ("Ivan", "2"),
    ("Max", "3"),
    ("Sam", "4"),
    ("Nikita", "5"),
    ("Sergey", "6"),
    ("Kirill", "7"),
    ("Georgiy", "8"),
]

# Each next user should be placed first after sort by rating
TEST_DATA_PLAYERS = [
    Player("Anton", "NMD_Anton", 100, 100),
    Player("Ivan", "NMD_Ivan", 200, 100),
    Player("Max", "NMD_Max", 300, 100),
    Player("Sam", "NMD_Sam", 400, 100),
    Player("Nikita", "NMD_Nikita", 500, 100),
    Player("Sergey", "NMD_Sergey", 600, 100),
    Player("Kirill", "NMD_Kirill", 700, 100),
    Player("Georgiy", "NMD_Georgiy", 800, 100),
]

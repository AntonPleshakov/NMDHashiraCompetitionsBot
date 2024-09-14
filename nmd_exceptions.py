class UsernameAlreadyExistsError(Exception):
    pass


class PlayerNotFoundError(Exception):
    pass


class MatchWithPlayersNotFound(Exception):
    pass


class TechWinCannotBeChanged(Exception):
    pass


class MatchResultWasAlreadyRegistered(Exception):
    pass


class MatchResultTryingToBeChanged(Exception):
    pass


class TournamentNotStartedError(Exception):
    pass


class TournamentStartedError(Exception):
    pass


class TournamentFinishedError(Exception):
    pass


class TournamentNotFinishedError(Exception):
    pass


class NewPlayerError(Exception):
    pass


class PairingCantFindByePlayer(Exception):
    pass


class PairingNoPlayers(Exception):
    pass

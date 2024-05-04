class UsernameAlreadyExistsError(Exception):
    pass


class PlayerNotFoundError(Exception):
    pass


class MatchWithPlayersNotFound(Exception):
    pass


class MatchResultWasAlreadyRegistered(Exception):
    pass


class TournamentNotStartedError(Exception):
    pass


class TournamentStartedError(Exception):
    pass


class TournamentFinishedError(Exception):
    pass

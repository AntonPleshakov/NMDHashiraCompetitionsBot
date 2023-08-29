def update_elo(winner_elo, loser_elo, k_winner, k_loser):
    expected_winner_win = expected_result(winner_elo, loser_elo)
    expected_loser_win = expected_result(loser_elo, winner_elo)
    winner_elo += k_winner * (1 - expected_winner_win)
    loser_elo += k_loser * (0 - expected_loser_win)
    return winner_elo, loser_elo


def expected_result(elo_a, elo_b, elo_width=400):
    expect_a = 1.0 / (1 + 10 ** ((elo_b - elo_a) / elo_width))
    return expect_a

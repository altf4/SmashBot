import melee

"""Holds all we need to keep track of the score of a match of melee"""
class ScoreState:
    ai_percent = 0
    opponent_percent = 0
    ai_stock = 4
    opponent_stock = 4

    def update(self, gamestate):
        self.ai_percent = gamestate.ai_state.percent
        self.ai_stock = gamestate.ai_state.stock
        self.opponent_percent = gamestate.opponent_state.percent
        self.opponent_stock = gamestate.opponent_state.stock

    """Score is determined by stocks and percents.
        Every stock is worth 1000 points, and each percent is worth
        a decreasing amount as it goes higher.
        IE: Hitting your opponent from 300% to 301% is worth less than hitting
        your opponent from 0% to 1%."""
    def score(self):
        #Each stock is worth 1000 points
        score = (4 - self.opponent_stock) * 1000
        score -= (4 - self.ai_stock) * 1000
        #Percent is worth a rapidly decreasing amount, approaching 1000
        #This will produce a value in the range of 0-1000, but with highly
        #diminishing returns
        #Some examples:
        # 50% = 368.403149864
        # 100% = 464.158883361
        # 150% = 531.329284591
        #As you can see, by 150%, we've already received half the max reward
        score += 100 * self.opponent_percent**(1/3)
        score -= 100 * self.ai_percent**(1/3)
        return score

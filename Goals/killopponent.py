from Goals import goal
import melee
import globals
import Strategies

class KillOpponent(goal.Goal):
    def step(self):
        # If the opponent is invincible, don't attack them. Just dodge everything they do
        # UNLESS they are invincible due to rolling on the stage.
        # Then go ahead and punish it, it will be safe by the time they are back up.
        smashbot_state = globals.smashbot_state
        if smashbot_state.invulnerable and \
            smashbot_state.action != melee.enums.Action.EDGE_GETUP_SLOW and \
            smashbot_state.action != EDGE_GETUP_QUICK and \
            smashbot_state.action != EDGE_ROLL_SLOW and \
            smashbot_state.action != EDGE_ROLL_QUICK:
                self.pickstrategy(Strategies.Sandbag)
        else:
            self.pickstrategy(Strategies.Bait)

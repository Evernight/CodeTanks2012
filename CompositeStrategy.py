def make_composite_strategy(move_strategy, targeting_strategy):

    class ResultStrategy:
        def __init__(self, move_strategy, targeting_strategy):
            self.move_strategy = move_strategy
            self.targeting_strategy = targeting_strategy

        def change_state(self, *args, **kwargs):
            self.move_strategy.change_state(*args, **kwargs)
            self.targeting_strategy.change_state(*args, **kwargs)

        def make_turn(self, move):
            self.move_strategy.EA_cache = {}
            self.move_strategy.make_turn(move)
            self.targeting_strategy.EA_cache = self.move_strategy.EA_cache
            self.targeting_strategy.make_turn(move)

    return ResultStrategy(move_strategy, targeting_strategy)

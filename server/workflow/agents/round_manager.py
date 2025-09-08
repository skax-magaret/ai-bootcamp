from workflow.state import RealEstateState


class RoundManager:
    def run(self, state: RealEstateState) -> RealEstateState:
        return self.increment_round(state)

    def increment_round(self, state: RealEstateState) -> RealEstateState:
        new_state = state.copy()
        new_state["current_round"] = state["current_round"] + 1
        return new_state

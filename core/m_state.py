class StateManager:
    def __init__(self, current_state):
        self.current_state = current_state

    def change_state(self, state):
        self.current_state = state
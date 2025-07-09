from connection_states.state_base import StateBase


class StateConnectionClosed(StateBase):
    def __init__(self):
        super().__init__()
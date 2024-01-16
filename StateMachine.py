import Player
from typing import Dict
from typing import List
from typing import Callable

class StateMachine:
    class State:
        def __init__(self, name:str, in_function:Callable, behaviour:Callable) -> None:
            self.name = name
            self.in_function = in_function
            self.behaviour = behaviour
            self.transitions:List[(Callable, str)] = []

    def __init__(self, player) -> None:
        self.player:Player.Player = player
        self.states:Dict[str, StateMachine.State] = {}
        self.current_state:StateMachine.State = None

    def add_state(self, name:str, in_function:Callable, behaviour:Callable) -> None:
        if name in self.states.keys():
            raise KeyError("State already defined")
        self.states[name] = StateMachine.State(name, in_function, behaviour)

    def add_transition(self, transition_function:Callable,state_to_change_from_name:str, state_to_change_to_name:str):
        if state_to_change_from_name not in self.states.keys():
            raise KeyError("State from not in the defined states")
        if state_to_change_to_name not in self.states.keys():
            raise KeyError("State to not in the defined states")
        
        self.states[state_to_change_from_name].transitions.append((transition_function, state_to_change_to_name))

    def check_state_change(self) -> None:
        for transition in self.current_state.transitions:
            transition_function:Callable = transition[0]
            transition_state_name = transition[1]
            if transition_function():
                self.change_current_state(self.states[transition_state_name])

    def change_current_state(self, new_state:State|str):
        if type(new_state) is str:
            self.current_state = self.states[new_state]
        else:
            self.current_state = new_state
        if self.current_state.in_function is not None:
            self.current_state.in_function(self.player)


    def behave(self, deltaTime):
        if self.current_state.behaviour is not None:
            self.current_state.behaviour(deltaTime)
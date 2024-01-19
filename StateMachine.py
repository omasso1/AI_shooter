import Player
from typing import Dict
from typing import List
from typing import Callable

class StateMachine:
    class State:
        def __init__(self, name:str, in_function:Callable, out_function:Callable, behaviour:Callable) -> None:
            self.name = name
            self.in_function = in_function
            self.behaviour = behaviour
            self.out_function = out_function
            self.transitions:List[(Callable, str)] = []

    def __init__(self, player) -> None:
        self.player:Player.Player = player
        self.states:Dict[str, StateMachine.State] = {}
        self.current_state:StateMachine.State = None

    def add_state(self, name:str, in_function:Callable, out_function:Callable, behaviour:Callable) -> None:
        if name in self.states.keys():
            raise KeyError("State already defined")
        self.states[name] = StateMachine.State(name, in_function, out_function, behaviour)

    def add_transition(self, transition_function:Callable,state_to_change_from_name:str, state_to_change_to_name:str):
        if not state_to_change_from_name in self.states.keys():
            raise KeyError("State from not in the defined states")
        if not state_to_change_to_name in self.states.keys():
            raise KeyError("State to not in the defined states")
        
        self.states[state_to_change_from_name].transitions.append((transition_function, state_to_change_to_name))

    def check_state_change(self) -> None:
        if self.current_state is None:
            return
        for transition in self.current_state.transitions:
            transition_function:Callable = transition[0]
            transition_state_name = transition[1]
            if transition_function():
                self.change_current_state(self.states[transition_state_name])

    def change_current_state(self, new_state:State|str):
        if self.current_state is not None and self.current_state.out_function is not None:
            self.current_state.out_function()

        if type(new_state) is str:
            self.current_state = self.states[new_state]
            print(f"Player color {self.player.color} change state to {new_state}")
        else:
            self.current_state = new_state
            print(f"Player color {self.player.color} change state to {new_state.name}")
        if self.current_state.in_function is not None:
            self.current_state.in_function()


    def behave(self, deltaTime):
        if self.current_state is None:
            return
        if self.current_state.behaviour is not None:
            self.current_state.behaviour(deltaTime)
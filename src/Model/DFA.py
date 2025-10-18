

from typing import Dict, Set, Optional
from Repository.TokenType import TokenType
from Model.State import State   # karena nama classnya State, tapi fokusnya di DFA, jadi diimport sebagai State


class DFA:# DFA
    # state, transisi, scanning
    def __init__(self):
        self.states: Dict[str, State] = {} # dict {nama state : objek state}
        self.startState: Optional[State] = None
        self.finalStates: Set[State] = set()
        self.keywords = set()
    
    def addState(self, name: str, isFinal: bool = False, tokenType: Optional[TokenType] = None) -> State:
        state = State(name, isFinal, tokenType)
        self.states[name] = state
        if isFinal: # kalo udah final state, masukin ke set final states
            self.finalStates.add(state)
        return state
    
    def setStartState(self, stateName: str):
        if stateName in self.states: # setter start state. (harus udah ada di states)
            self.startState = self.states[stateName]
    
    def addTransition(self, fromState: str, inputChar: str, toState: str):
        if fromState in self.states and toState in self.states: # menambahkan transisi antar state (harus udah ada di states)
            self.states[fromState].addTransition(inputChar, self.states[toState])
    
    def getCurrentState(self) -> State:
        # Mendapatkan current state (DFA selalu mulai dari start state)
        return self.startState
    
    def isKeyword(self, lexeme: str) -> bool:
        return lexeme.lower() in self.keywords
    
    def getTokenType(self, lexeme: str, finalState: State) -> TokenType:
        if finalState.tokenType:
            if finalState.tokenType == TokenType.IDENTIFIER and self.isKeyword(lexeme):
                return TokenType.KEYWORD
            return finalState.tokenType
        if self.isKeyword(lexeme):
            return TokenType.KEYWORD
        elif lexeme.isdigit():
            return TokenType.NUMBER
        elif lexeme.isalpha() or '_' in lexeme:
            return TokenType.IDENTIFIER
        else:
            return TokenType.UNKNOWN  
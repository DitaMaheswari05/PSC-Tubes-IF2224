

from typing import Dict, Set, Optional
from Repository.TokenType import TokenType

class DFAState:
    def __init__(self, name: str, isFinal: bool = False, tokenType: Optional[TokenType] = None):
        self.name = name
        self.isFinal = isFinal # kalo finalstate, tokenType harus diisi
        self.tokenType = tokenType # tipe token
        self.transitions: Dict[str, 'DFAState'] = {} #input char, next state
    
    def addTransition(self, inputChar: str, nextState: 'DFAState'):
        self.transitions[inputChar] = nextState 
    
    def getNextState(self, inputChar: str) -> Optional['DFAState']:
        return self.transitions.get(inputChar)

class DFA:# DFA
    # state, transisi, scanning
    
    def __init__(self):
        self.states: Dict[str, DFAState] = {} # dict {nama state : objek state}
        self.startState: Optional[DFAState] = None
        self.finalStates: Set[DFAState] = set()
        self.keywords = set()
    
    def addState(self, name: str, isFinal: bool = False, tokenType: Optional[TokenType] = None) -> DFAState:
        state = DFAState(name, isFinal, tokenType)
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
    
    def getCurrentState(self) -> DFAState:
        # Mendapatkan current state (DFA selalu mulai dari start state)
        return self.startState
    
    def isKeyword(self, lexeme: str) -> bool:
        return lexeme.lower() in self.keywords
    
    def getTokenType(self, lexeme: str, finalState: DFAState) -> TokenType:
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
from typing import Dict, Optional

from Repository.TokenType import TokenType

class State:
    def __init__(self, name: str, isFinal: bool = False, tokenType: Optional[TokenType] = None):
        self.name = name
        self.isFinal = isFinal # kalo finalstate, tokenType harus diisi
        self.tokenType = tokenType # tipe token
        self.transitions: Dict[str, 'State'] = {} #input char, next state

    def addTransition(self, inputChar: str, nextState: 'State'): # 
        self.transitions[inputChar] = nextState

    def getNextState(self, inputChar: str) -> Optional['State']:
        return self.transitions.get(inputChar)
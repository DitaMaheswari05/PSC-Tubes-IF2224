from typing import Dict, Any
from Model.DFA import DFA
from Repository.TokenType import TokenType
from Repository.JSONParser import JSONParser


class DFAParser:
    def __init__(self):
        self.jsonParser = JSONParser()
    
    def parseDFAFromJSON(self, filePath: str) -> DFA:
        # keseluruhan fungsi dari class DFAParser: membaca file JSON dan membuat DFA
        jsonContent = self.jsonParser.parseFile(filePath)
        dfaData = self.jsonParser.parseJSON(jsonContent)
        return self.buildDFA(dfaData)
    
    def buildDFA(self, dfaData: Dict[str, Any]) -> DFA:
        # buat DFA dari data JSON
        dfa = DFA()
        
        # Parse states
        if 'states' in dfaData:
            for stateName, stateInfo in dfaData['states'].items():
                isFinal = stateInfo.get('is_final', False)
                tokenTypeName = stateInfo.get('token_type')
                tokenType = None
                
                if tokenTypeName and hasattr(TokenType, tokenTypeName):
                    tokenType = getattr(TokenType, tokenTypeName)
                
                dfa.addState(stateName, isFinal, tokenType)
        
        if 'start_state' in dfaData:
            dfa.setStartState(dfaData['start_state'])
        
        if 'transitions' in dfaData:
            for transition in dfaData['transitions']:
                fromState = transition.get('from')
                inputChar = transition.get('input')
                toState = transition.get('to')
                
                if fromState and inputChar and toState:
                    dfa.addTransition(fromState, inputChar, toState)
        
        return dfa
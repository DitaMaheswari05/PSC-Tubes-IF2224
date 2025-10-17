import json
from typing import Dict, Any
from Model.DFA import DFA
from Repository.JSONParser import JSONParser
from Repository.DFAParser import DFAParser
    
class Parser(JSONParser):
    def __init__(self):
        super().__init__()
        self.dfaParser = DFAParser()
    
    def parseDFA(self, filePath: str) -> DFA:
        if filePath.endswith('.json'): # intinya ngecek ekstensi file 
            return self.dfaParser.parseDFAFromJSON(filePath)
        else:
            raise ValueError("cuman bisa DFA basis JSON")


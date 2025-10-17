import json 
from typing import Dict, Any

class JSONParser: # parser untuk file json
    
    def parseFile(self, filePath: str) -> str:
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"{filePath} gaada")
        except Exception as e:
            raise Exception(f"gabisa baca file {filePath}: {str(e)}")
    
    def parseJSON(self, jsonString: str) -> Dict[str, Any]:
        try:
            return json.loads(jsonString)
        except json.JSONDecodeError as e:
            raise ValueError(f"invalid JSONformat: {str(e)}")
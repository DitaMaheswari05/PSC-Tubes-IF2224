import json
import sys
from typing import Dict, Any

class DFASpec:
    # Memuat dan menyediakan akses ke spesifikasi DFA dari file JSON
    def __init__(self, spec: Dict[str, Any]):
        self.start_state: str = spec['start_state']
        self.states: Dict[str, Any] = spec['states']
        self.reserved_words: Dict[str, str] = spec['reserved_words']

    @classmethod
    def from_file(cls, filepath: str) -> 'DFASpec':
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return cls(json.load(f))
        except FileNotFoundError:
            print(f"Error: File spesifikasi DFA tidak ditemukan di '{filepath}'")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Gagal mem-parsing file JSON '{filepath}'. Periksa formatnya.")
            sys.exit(1)
        except Exception as e:
            print(f"Gagal memuat {filepath}: {e}")
            sys.exit(1)
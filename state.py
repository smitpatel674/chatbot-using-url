from typing import List, Tuple, Optional
from crawler import SiteKB

class AppState:
    def __init__(self):
        self.kb: Optional[SiteKB] = None
        self.history: List[Tuple[str, str]] = []
        self.model_name: str = "gemini-1.5-flash"
        self.model = None
        self.language: str = "English"

    def reset(self):
        self.kb = None
        self.history = []
        self.model = None

STATE = AppState()

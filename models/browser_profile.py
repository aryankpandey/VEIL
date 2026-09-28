from dataclasses import dataclass

@dataclass
class BrowserProfile:
    id: str
    name: str
    is_private: bool

from dataclasses import dataclass
from datetime import datetime

@dataclass
class HistoryEntry:
    id: int
    url: str
    title: str
    visit_time: datetime
    profile_id: str

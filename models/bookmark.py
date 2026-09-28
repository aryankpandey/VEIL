from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class BookmarkFolder:
    id: int
    name: str
    parent_id: Optional[int]
    profile_id: str

@dataclass
class Bookmark:
    id: int
    title: str
    url: str
    folder_id: Optional[int]
    profile_id: str
    created_at: datetime

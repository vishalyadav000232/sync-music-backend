import asyncio
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RoomState:
    pubsub: object                        
    task: Optional[asyncio.Task] = None  
    ref_count: int = 0   
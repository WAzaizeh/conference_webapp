import asyncio
import json
from typing import Dict, Set
from collections import defaultdict
from dataclasses import dataclass, asdict

@dataclass
class SSEMessage:
    """Represents an SSE message"""
    event: str
    data: dict
    
    def format(self) -> str:
        """Format as SSE message"""
        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"

class SSEManager:
    """Manages Server-Sent Events for Q&A updates"""
    
    def __init__(self):
        # Dictionary mapping event_id -> set of queues
        self._connections: Dict[int, Set[asyncio.Queue]] = defaultdict(set)
    
    async def subscribe(self, event_id: int) -> asyncio.Queue:
        """Subscribe to updates for a specific event"""
        queue = asyncio.Queue(maxsize=100)
        self._connections[event_id].add(queue)
        return queue
    
    def unsubscribe(self, event_id: int, queue: asyncio.Queue):
        """Unsubscribe from updates"""
        if event_id in self._connections:
            self._connections[event_id].discard(queue)
            if not self._connections[event_id]:
                del self._connections[event_id]
    
    async def broadcast(self, event_id: int, message: SSEMessage):
        """Broadcast a message to all subscribers of an event"""
        if event_id not in self._connections:
            return
        
        # Create list to avoid modification during iteration
        queues = list(self._connections[event_id])
        
        for queue in queues:
            try:
                # Non-blocking put with timeout
                await asyncio.wait_for(queue.put(message), timeout=1.0)
            except asyncio.TimeoutError:
                # Remove slow consumers
                self.unsubscribe(event_id, queue)
            except Exception:
                # Remove failed queues
                self.unsubscribe(event_id, queue)
    
    async def send_question_update(self, event_id: int, question_data: dict, action: str):
        """Send a question update (new, updated, deleted)"""
        message = SSEMessage(
            event="question_update",
            data={
                "action": action,  # "created", "updated", "deleted"
                "question": question_data
            }
        )
        await self.broadcast(event_id, message)
    
    async def send_like_update(self, event_id: int, question_id: str, likes_count: int):
        """Send a like count update"""
        message = SSEMessage(
            event="like_update",
            data={
                "question_id": question_id,
                "likes_count": likes_count
            }
        )
        await self.broadcast(event_id, message)

# Global SSE manager instance
sse_manager = SSEManager()

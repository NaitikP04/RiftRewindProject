"""
Progress streaming for long-running analysis.
Allows frontend to see real-time backend progress.
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from datetime import datetime

class ProgressTracker:
    """Thread-safe progress tracker for streaming updates."""
    
    def __init__(self):
        self.subscribers: Dict[str, asyncio.Queue] = {}
        self.progress: Dict[str, Dict[str, Any]] = {}
    
    def subscribe(self, analysis_id: str) -> asyncio.Queue:
        """Subscribe to progress updates for an analysis."""
        queue = asyncio.Queue()
        self.subscribers[analysis_id] = queue
        return queue
    
    def unsubscribe(self, analysis_id: str):
        """Unsubscribe from progress updates."""
        if analysis_id in self.subscribers:
            del self.subscribers[analysis_id]
        if analysis_id in self.progress:
            del self.progress[analysis_id]
    
    async def update(self, analysis_id: str, step: str, progress: int, message: str):
        """Send progress update to all subscribers."""
        update = {
            "step": step,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store latest progress
        self.progress[analysis_id] = update
        
        # Send to subscriber if exists
        if analysis_id in self.subscribers:
            try:
                await self.subscribers[analysis_id].put(update)
            except:
                pass  # Subscriber disconnected
    
    async def stream_progress(self, analysis_id: str) -> AsyncGenerator[str, None]:
        """Stream progress updates as Server-Sent Events."""
        queue = self.subscribe(analysis_id)
        
        try:
            while True:
                # Wait for next update with timeout
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(update)}\n\n"
                except asyncio.TimeoutError:
                    # Send keep-alive
                    yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
        finally:
            self.unsubscribe(analysis_id)

# Global progress tracker
progress_tracker = ProgressTracker()

"""Event system for cbhands v3.0.0."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading


@dataclass
class Event:
    """Event data structure."""
    type: str
    data: Any
    source: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class EventBus:
    """Event bus for plugin communication."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize event bus."""
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.RLock()
        self._enabled = True
    
    def subscribe(self, event_type: str, handler: Callable, async_handler: bool = False) -> None:
        """Subscribe to an event type."""
        with self._lock:
            if async_handler:
                self._async_handlers[event_type].append(handler)
            else:
                self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type."""
        with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
            if handler in self._async_handlers[event_type]:
                self._async_handlers[event_type].remove(handler)
    
    def emit(self, event_type: str, data: Any, source: Optional[str] = None) -> None:
        """Emit an event synchronously."""
        if not self._enabled:
            return
        
        event = Event(type=event_type, data=data, source=source)
        
        with self._lock:
            # Execute synchronous handlers
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
            
            # Execute asynchronous handlers in thread pool
            for handler in self._async_handlers[event_type]:
                self._executor.submit(self._run_async_handler, handler, event)
    
    async def emit_async(self, event_type: str, data: Any, source: Optional[str] = None) -> None:
        """Emit an event asynchronously."""
        if not self._enabled:
            return
        
        event = Event(type=event_type, data=data, source=source)
        
        with self._lock:
            # Execute synchronous handlers
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")
            
            # Execute asynchronous handlers
            tasks = []
            for handler in self._async_handlers[event_type]:
                tasks.append(self._run_async_handler_await(handler, event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def _run_async_handler(self, handler: Callable, event: Event) -> None:
        """Run async handler in thread pool."""
        try:
            if asyncio.iscoroutinefunction(handler):
                asyncio.run(handler(event))
            else:
                handler(event)
        except Exception as e:
            print(f"Error in async event handler for {event.type}: {e}")
    
    async def _run_async_handler_await(self, handler: Callable, event: Event) -> None:
        """Run async handler with await."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            print(f"Error in async event handler for {event.type}: {e}")
    
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Get all subscribers for an event type."""
        with self._lock:
            return (self._handlers[event_type] + self._async_handlers[event_type]).copy()
    
    def get_event_types(self) -> List[str]:
        """Get all registered event types."""
        with self._lock:
            return list(set(self._handlers.keys()) | set(self._async_handlers.keys()))
    
    def clear(self) -> None:
        """Clear all handlers."""
        with self._lock:
            self._handlers.clear()
            self._async_handlers.clear()
    
    def disable(self) -> None:
        """Disable event bus."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable event bus."""
        self._enabled = True
    
    def shutdown(self) -> None:
        """Shutdown event bus."""
        self._enabled = False
        self._executor.shutdown(wait=True)
        self.clear()

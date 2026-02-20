from __future__ import annotations
from collections import namedtuple, deque

Event = namedtuple('Event', ['type', 'data'])

def create_key_event(key_code: int, char: str | None = None) -> Event:
    return Event('key', {'code': key_code, 'char': char})

def MouseEvent(x: int, y: int, button: int, event_type: str) -> Event:
    return Event('mouse', {'x': x, 'y': y, 'button': button, 'event_type': event_type})

def CustomEvent(name: str, payload: dict | None = None) -> Event:
    return Event(name, payload if payload is not None else {})

class EventDispatcher:
    _instance: 'EventDispatcher' | None = None

    def __new__(cls) -> 'EventDispatcher':
        if cls._instance is None:
            cls._instance = super(EventDispatcher, cls).__new__(cls)
            cls._instance.handlers: dict[str, list[callable]] = {}
        return cls._instance

    def register_handler(self, event_type: str, handler_func: callable) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler_func)

    def dispatch(self, event: Event) -> None:
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)

    def post(self, event: Event) -> None:
        _global_event_queue.append(event)

_global_event_queue: deque[Event] = deque()

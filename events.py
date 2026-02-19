from collections import namedtuple, deque

Event = namedtuple('Event', ['type', 'data'])
"""Base class for TUI events."""

def create_key_event(key_code, char=None): return Event('key', {'code': key_code, 'char': char})
"""Represents a keyboard event."""

MouseEvent = lambda x, y, button, event_type: Event('mouse', {'x': x, 'y': y, 'button': button, 'event_type': event_type})
CustomEvent = lambda name, payload=None: Event(name, payload if payload is not None else {})

class EventDispatcher:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventDispatcher, cls).__new__(cls)
            cls._instance.handlers = {}
        return cls._instance

    def register_handler(self, event_type, handler_func):
        """Registers a function to handle events of a specific type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler_func)

    def dispatch(self, event):
        """Dispatches an event to all registered handlers for its type."""
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)

    def post(self, event):
        """Adds an event to the global event queue for later dispatch."""
        _global_event_queue.append(event)

_global_event_queue = deque()

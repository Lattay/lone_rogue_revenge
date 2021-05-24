import pygame


class Action:
    pass


class EventHandler:
    def __init__(self):
        self.handlers = {}

    def register(self, event_type, action):
        def decorator(test):
            self.handlers.setdefault(event_type, []).append((test, action))
            return test

        return decorator

    def handle_events(self, state):
        for test, action in self.handlers[None]:
            if test(state):
                setattr(state, action, True)

        for event in pygame.event.get():
            if event.type in self.handlers:
                for test, action in self.handlers[event.type]:
                    if test(state, event):
                        setattr(state, action, True)


handler = EventHandler()


class ActionStates:
    def __init__(self):
        super().__init__()
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.fire = False
        self.ui_select = False
        self.ui_back = False
        self.quit = False

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            return False

_ui_layouts = {}


def load_ui(layout, group):
    return _ui_layouts[layout](group)


def register_ui(key):
    def wrapper(f):
        _ui_layouts[key] = f
        return f
    return wrapper

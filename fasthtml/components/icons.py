from fasthtml.components import I

def Icon(name : str, cls : str = '', **kwargs) -> I:
    return I(cls=f'fas fa-{name}' + (' '  + cls if cls else ''), **kwargs)
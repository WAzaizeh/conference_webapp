from components.icon import Icon
from fasthtml.components import A,Div, Button, Span

def BottomNav() -> Div:
    return Div(
        # <span class=>
        A(Span('home', cls='material-symbols-rounded'), 'Home', cls='nav-item', href='/'),
        A(Span('calendar_today', cls='material-symbols-rounded'), 'Agenda', cls='nav-item', href='/agenda'),
        A(Span('mic', cls='material-symbols-rounded'), 'Speakers', cls='nav-item', href='/speakers'),
        # A(Span('handshake', cls='material-symbols-rounded'), 'Settings', cls='nav-item', href='#'),
        A(Span('handshake', cls='material-symbols-rounded'), 'Sponsors', cls='nav-item', href='/sponsors'),
        cls='btm-nav'
    )

def BackButton(**kwargs) -> Button:
    return Button(
        Icon('arrow-left'),
        cls='btn btn-ghost fixed left-0' + kwargs.get('cls', ''),
        onclick='goBack()'
        )
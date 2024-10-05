from components.icon import Icon
from fasthtml.components import A,Div, Button, Span, H1

def BottomNav(active_button_index: int = None) -> Div:
    return Div(
        A(Span('home', cls='material-symbols-rounded'), 'Home', cls=f"nav-item {'active' if active_button_index==1 else ''}", href='/'),
        A(Span('calendar_today', cls='material-symbols-rounded'), 'Agenda', cls=f"nav-item {'active' if active_button_index==2 else ''}", href='/agenda'),
        A(Span('mic', cls='material-symbols-rounded'), 'Speakers', cls=f"nav-item {'active' if active_button_index==3 else ''}", href='/speakers'),
        A(Span('handshake', cls='material-symbols-rounded'), 'Sponsors', cls=f"nav-item {'active' if active_button_index==4 else ''}", href='/sponsors'),
        cls='btm-nav'
    )

def BackButton(**kwargs) -> Button:
    return Button(
        Icon('chevron-left'),
        cls='btn btn-ghost' + kwargs.get('cls', ''),
        onclick='goBack()'
        )

def TopNav(title: int = None) -> Div:
    return  Div(
                BackButton(),
                H1(title, cls='flex-1 text-black font-medium text-center text-base top-nav-title'),
                cls='flex justify-center items-center p-4 top-nav',
            ),
from fasthtml.components import Div, Html
from components.titled import CustomTitled
from components.navigation import BottomNav

def AppContainer(content: Div) -> Div:
    return CustomTitled('MAS CYP Conference 2024',
                Html(data_theme='cupcake'),
                Div(
                    content,
                    Div(cls="ghost-btm-nav"),
                    BottomNav(),
                    cls='flex-container'
                )
            )
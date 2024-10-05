from fasthtml.components import Div, Html
from components.titled import CustomTitled
from components.navigation import BottomNav

def AppContainer(content: Div, active_button_index: int) -> Div:
    return CustomTitled('MAS CYP Conference 2024',
                Html(data_theme='cupcake'),
                content,
                BottomNav(active_button_index),
            )
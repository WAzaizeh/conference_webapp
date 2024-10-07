from db.data import SPONSORS
from crud.core import get_sponsor
from fasthtml.components import Div, H1
from components.page import AppContainer
from fasthtml.common import RedirectResponse
from components.cards import brief_sponsor_card, sponsor_page

def get_sponsor_routes(rt):
    @rt('/sponsors')
    def get():
        return AppContainer(
                Div(
                    Div(
                        H1('Sponsors', cls='flex-1 text-black font-medium text-center text-base'),
                        cls='flex justify-center items-center p-4',
                    ),
                *[brief_sponsor_card(sponsor) for sponsor in SPONSORS],
                cls='blue-background',
                id='page-content',
            ),
            active_button_index=4
        )

    @rt('/sponsors/{sponsor_id}')
    def get(sponsor_id: int):
        speaker = get_sponsor(sponsor_id)
        if speaker:
            return AppContainer(
                Div(
                sponsor_page(speaker),
                id='page-content',
                ),
                active_button_index=4
            )
        return RedirectResponse('/sponsors', status_code=303)
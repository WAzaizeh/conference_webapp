from crud.core import get_sponsor
from fasthtml.components import Div, H1
from components.page import AppContainer
from fasthtml.common import RedirectResponse
from components.cards import brief_sponsor_card, sponsor_page
from db.service import db_service

def get_sponsor_routes(rt):
    @rt('/sponsors')
    def get():
        sponsors = db_service.get_all_sponsors()
        return AppContainer(
                Div(
                    Div(
                        H1('Sponsors', cls='flex-1 text-black font-medium text-center text-base'),
                        cls='flex justify-center items-center p-4',
                    ),
                *[brief_sponsor_card(sponsor) for sponsor in sponsors],
                cls='blue-background',
                id='page-content',
            ),
            active_button_index=4
        )

    @rt('/sponsors/{sponsor_id}')
    def get(sponsor_id: int):
        sponsor = db_service.get_sponsor_by_id(sponsor_id)
        if sponsor:
            return AppContainer(
                Div(
                sponsor_page(sponsor),
                id='page-content',
                ),
                active_button_index=4
            )
        return RedirectResponse('/sponsors', status_code=303)
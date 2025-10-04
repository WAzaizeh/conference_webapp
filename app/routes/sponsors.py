from fasthtml.components import Div, H1
from components.page import AppContainer
from fasthtml.common import RedirectResponse
from components.cards import brief_sponsor_card, sponsor_page
from crud.sponsor import get_sponsors, get_sponsor
from db.connection import db_manager

def get_sponsor_routes(rt):
    @rt('/sponsors')
    async def get():
        async with db_manager.AsyncSessionLocal() as db_session:
            sponsors = await get_sponsors(db_session)
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
    async def get(sponsor_id: int):
        async with db_manager.AsyncSessionLocal() as db_session:
            sponsor = await get_sponsor(db_session, sponsor_id)
        if sponsor:
            return AppContainer(
                Div(
                sponsor_page(sponsor),
                id='page-content',
                ),
                active_button_index=4
            )
        return RedirectResponse('/sponsors', status_code=303)
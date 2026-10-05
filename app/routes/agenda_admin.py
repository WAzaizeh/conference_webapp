from datetime import datetime, timedelta, timezone
from typing import List, Optional
from components.icon import Icon
from components.navigation import TopNav
from components.page import AppContainer
from fasthtml.common import RedirectResponse, Response
from fasthtml.components import A, Button, Div, Form, H2, Img, Input, Label, Option, P, Select, Span, Textarea
from core.app import rt
from crud.event import create_event, delete_event, get_event, get_events, update_event
from crud.speaker import get_speakers
from db.connection import db_manager
from db.models import Event, Speaker
from db.schemas import EventCreate, EventUpdate
from utils.auth import is_moderator, require_moderator

CATEGORIES = ['MAIN', 'TALK', 'PANEL DISCUSSION', 'WORKSHOP', 'LIGHTNING_TALK', 'PRESENTATION', 'ACTIVITY', 'BREAK', 'PRAYER']
DEFAULT_LOCATION = 'GEM Academy & Facility'
DEFAULT_START = datetime(2026, 10, 24, 11, 0, tzinfo=timezone.utc)
INPUT_DT_FORMAT = '%Y-%m-%dT%H:%M'

# Event times are stored as conference wall-clock time tagged as UTC (e.g. 11:00 AM -> 11:00+00:00),
# which is how the agenda page displays them, so form values are converted without any tz shift.
def _to_input(dt: datetime) -> str:
    return dt.strftime(INPUT_DT_FORMAT)

def _from_input(value: str) -> datetime:
    return datetime.strptime(value, INPUT_DT_FORMAT).replace(tzinfo=timezone.utc)

def _time_range(event: Event) -> str:
    return f'{event.start_time.strftime("%a %b %d · %I:%M %p")} – {event.end_time.strftime("%I:%M %p")}'


def agenda_admin_row(event: Event) -> Div:
    return Div(
        Div(
            Span(_time_range(event), cls='text-xs text-primary font-medium'),
            Span(event.category or 'MAIN', cls='badge badge-sm badge-outline'),
            cls='flex justify-between items-center gap-2 flex-wrap',
        ),
        P(event.title, cls='font-semibold'),
        P(
            Icon('location-dot', cls='mr-1'), event.location or '—',
            Span(' · ', cls='mx-1'),
            Icon('microphone', cls='mr-1'), ', '.join(s.name for s in event.speakers) or 'No speakers',
            cls='text-xs opacity-70',
        ),
        Div(
            A(Icon('pen', cls='mr-1'), 'Edit', href=f'/admin/agenda/{event.id}', cls='btn btn-sm btn-primary'),
            Form(
                Button(Icon('trash', cls='mr-1'), 'Delete', type='submit', cls='btn btn-sm btn-outline btn-error'),
                method='post',
                action=f'/admin/agenda/{event.id}/delete',
                onsubmit=f"return confirm('Delete \"{event.title.replace(chr(39), '')}\"? Its Q&A questions will be deleted too.')",
            ),
            cls='flex gap-2 justify-end',
        ),
        cls='timeline-box p-4 flex flex-col gap-2',
    )


def agenda_form(action: str, speakers: List[Speaker], event: Optional[Event] = None,
                values: Optional[dict] = None, error: Optional[str] = None) -> Form:
    """Add/edit session form. `values` holds submitted data when re-rendering after a validation error."""
    if values is None:
        values = {
            'title': event.title if event else '',
            'description': (event.description or '') if event else '',
            'start_time': _to_input(event.start_time) if event else _to_input(DEFAULT_START),
            'end_time': _to_input(event.end_time) if event else _to_input(DEFAULT_START + timedelta(hours=1)),
            'location': (event.location or '') if event else DEFAULT_LOCATION,
            'category': (event.category or 'MAIN') if event else 'MAIN',
            'speaker_ids': [s.id for s in event.speakers] if event else [],
        }
    categories = CATEGORIES if values['category'] in CATEGORIES else [values['category'], *CATEGORIES]

    def field(label, control):
        return Label(Span(label, cls='label-text font-medium'), control, cls='form-control w-full gap-1')

    return Form(
        Div(Icon('exclamation-triangle', cls='mr-2'), Span(error), cls='alert alert-error') if error else None,
        field('Title', Input(name='title', value=values['title'], required=True, cls='input input-bordered w-full')),
        Div(
            field('Start', Input(name='start_time', type='datetime-local', value=values['start_time'], required=True, cls='input input-bordered w-full')),
            field('End', Input(name='end_time', type='datetime-local', value=values['end_time'], required=True, cls='input input-bordered w-full')),
            cls='grid grid-cols-1 sm:grid-cols-2 gap-4',
        ),
        Div(
            field('Location', Input(name='location', value=values['location'], cls='input input-bordered w-full')),
            field('Category', Select(
                *[Option(c.replace('_', ' ').title(), value=c, selected=c == values['category']) for c in categories],
                name='category', cls='select select-bordered w-full',
            )),
            cls='grid grid-cols-1 sm:grid-cols-2 gap-4',
        ),
        field('Description', Textarea(values['description'], name='description', rows=5, cls='textarea textarea-bordered w-full')),
        Div(
            Span('Speakers', cls='label-text font-medium'),
            Div(
                *[Label(
                    Input(type='checkbox', name='speaker_ids', value=str(s.id), checked=s.id in values['speaker_ids'], cls='checkbox checkbox-sm checkbox-primary'),
                    Img(src=s.image_url, alt='', cls='w-8 h-8 rounded-full object-cover'),
                    Span(s.name, cls='text-sm'),
                    cls='flex items-center gap-3 cursor-pointer py-1',
                ) for s in speakers] or [P('No speakers yet', cls='text-sm opacity-60')],
                cls='flex flex-col max-h-64 overflow-y-auto border border-base-300 rounded-lg px-3 py-2',
            ),
            cls='flex flex-col gap-1',
        ),
        Div(
            A('Cancel', href='/admin/agenda', cls='btn btn-ghost'),
            Button(Icon('save', cls='mr-1'), 'Save', type='submit', cls='btn btn-primary'),
            cls='flex justify-end gap-2',
        ),
        method='post',
        action=action,
        cls='flex flex-col gap-4 p-6 white-background',
    )


async def _parse_form(req):
    """Read and validate the session form. Returns (values, error)."""
    form = await req.form()
    values = {
        'title': (form.get('title') or '').strip(),
        'description': (form.get('description') or '').strip(),
        'start_time': form.get('start_time') or '',
        'end_time': form.get('end_time') or '',
        'location': (form.get('location') or '').strip(),
        'category': form.get('category') or 'MAIN',
        'speaker_ids': [int(i) for i in form.getlist('speaker_ids')],
    }
    if not values['title']:
        return values, 'Title is required.'
    try:
        start, end = _from_input(values['start_time']), _from_input(values['end_time'])
    except ValueError:
        return values, 'Start and end times are required.'
    if end <= start:
        return values, 'End time must be after start time.'
    return values, None


def _event_fields(values: dict) -> dict:
    return dict(
        title=values['title'],
        description=values['description'] or None,
        start_time=_from_input(values['start_time']),
        end_time=_from_input(values['end_time']),
        location=values['location'] or None,
        category=values['category'],
        speaker_ids=values['speaker_ids'],
    )


def _page(title: str, content, sess):
    return AppContainer(
        Div(TopNav(title), content, id='page-content', cls='blue-background'),
        is_moderator=is_moderator(sess),
    )


@rt('/admin/agenda')
@require_moderator
async def get(req, sess):
    """List all sessions with edit/delete actions"""
    async with db_manager.AsyncSessionLocal() as db:
        events = sorted(await get_events(db), key=lambda e: e.start_time)
    return _page('Edit Agenda', Div(
        Div(
            P(f'{len(events)} session{"s" if len(events) != 1 else ""}', cls='text-sm opacity-70'),
            A(Icon('plus', cls='mr-1'), 'Add session', href='/admin/agenda/new', cls='btn btn-sm btn-primary'),
            cls='flex justify-between items-center',
        ),
        *[agenda_admin_row(e) for e in events],
        cls='flex flex-col gap-4 p-6',
    ), sess)


@rt('/admin/agenda/new')
@require_moderator
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db:
        speakers = await get_speakers(db)
        events = await get_events(db)
    # Default a new session to start when the last 2026 session ends
    start = max([DEFAULT_START, *(e.end_time for e in events)])
    form = agenda_form('/admin/agenda/new', speakers, values={
        'title': '', 'description': '', 'location': DEFAULT_LOCATION, 'category': 'MAIN', 'speaker_ids': [],
        'start_time': _to_input(start), 'end_time': _to_input(start + timedelta(minutes=30)),
    })
    return _page('Add Session', form, sess)


@rt('/admin/agenda/new')
@require_moderator
async def post(req, sess):
    values, error = await _parse_form(req)
    async with db_manager.AsyncSessionLocal() as db:
        if error:
            return _page('Add Session', agenda_form('/admin/agenda/new', await get_speakers(db), values=values, error=error), sess)
        await create_event(db, EventCreate(**_event_fields(values)))
    return RedirectResponse('/admin/agenda', status_code=303)


@rt('/admin/agenda/{event_id}')
@require_moderator
async def get(req, sess, event_id: int):
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return RedirectResponse('/admin/agenda', status_code=303)
        speakers = await get_speakers(db)
    return _page('Edit Session', agenda_form(f'/admin/agenda/{event_id}', speakers, event=event), sess)


@rt('/admin/agenda/{event_id}')
@require_moderator
async def post(req, sess, event_id: int):
    values, error = await _parse_form(req)
    async with db_manager.AsyncSessionLocal() as db:
        if error:
            return _page('Edit Session', agenda_form(f'/admin/agenda/{event_id}', await get_speakers(db), values=values, error=error), sess)
        if not await update_event(db, event_id, EventUpdate(**_event_fields(values))):
            return Response('Session not found', status_code=404)
    return RedirectResponse('/admin/agenda', status_code=303)


@rt('/admin/agenda/{event_id}/delete')
@require_moderator
async def post(req, sess, event_id: int):
    async with db_manager.AsyncSessionLocal() as db:
        await delete_event(db, event_id)
    return RedirectResponse('/admin/agenda', status_code=303)

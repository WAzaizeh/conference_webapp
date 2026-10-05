from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from components.icon import Icon
from components.navigation import TopNav
from components.page import AppContainer
from fasthtml.common import RedirectResponse, Response, Script, Style
from fasthtml.components import A, Button, Dialog, Div, Form, H3, Img, Input, Label, Option, P, Select, Span, Textarea
from core.app import rt
from crud.event import create_event, delete_event, get_event, get_events, update_event
from crud.speaker import create_speaker, get_speakers
from db.connection import db_manager
from db.models import Event, Speaker, event_speakers
from db.schemas import EventCreate, EventUpdate, SpeakerCreate
from utils.auth import is_moderator, require_moderator

CATEGORIES = ['MAIN', 'TALK', 'PANEL DISCUSSION', 'WORKSHOP', 'LIGHTNING_TALK', 'PRESENTATION', 'ACTIVITY', 'BREAK', 'PRAYER']
DEFAULT_LOCATION = 'GEM Academy & Facility'
DEFAULT_START = datetime(2026, 10, 24, 11, 0, tzinfo=timezone.utc)
INPUT_DT_FORMAT = '%Y-%m-%dT%H:%M'
INPUT_TIME_FORMAT = '%H:%M'
INLINE_FIELDS = ('title', 'location', 'start_time', 'end_time', 'category', 'speakers')

# Event times are stored as conference wall-clock time tagged as UTC (e.g. 11:00 AM -> 11:00+00:00),
# which is how the agenda page displays them, so form values are converted without any tz shift.
def _to_input(dt: datetime) -> str:
    return dt.strftime(INPUT_DT_FORMAT)

def _from_input(value: str) -> datetime:
    return datetime.strptime(value, INPUT_DT_FORMAT).replace(tzinfo=timezone.utc)

def _category_label(category: Optional[str]) -> str:
    return (category or 'MAIN').replace('_', ' ').title()


ADMIN_CSS = """
.agenda-admin .editable {
    cursor: pointer;
    border-radius: 6px;
    padding: 1px 4px;
    margin: -1px -4px;
    transition: background-color .15s, box-shadow .15s;
}
.agenda-admin .editable:hover {
    background-color: rgba(0, 78, 163, .08);
    box-shadow: inset 0 0 0 1px rgba(0, 78, 163, .35);
}
.agenda-admin .editable.empty { opacity: .55; font-style: italic; }
.agenda-admin .inline-input { height: 2rem; min-height: 2rem; font-size: .875rem; }
"""

# Escape cancels an inline editor; the description dialog closes after a successful save
ADMIN_JS = """
function cancelAgendaEdit() {
    htmx.ajax('GET', '/admin/agenda/list', {target: '#agenda-list', swap: 'outerHTML'});
}
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && e.target.closest && e.target.closest('.inline-editor') && !e.target.closest('#description-modal')) cancelAgendaEdit();
});
document.addEventListener('htmx:afterRequest', (e) => {
    if (e.detail.successful && e.detail.elt.closest && e.detail.elt.closest('#description-modal')) {
        document.getElementById('description-modal').close();
    }
});
"""


def _editable(content, event_id: int, field: str, cls: str = '', title: str = 'Click to edit'):
    """Display element that swaps itself for an inline editor when clicked"""
    return Span(
        content,
        hx_get=f'/admin/agenda/{event_id}/edit/{field}',
        hx_target='this',
        hx_swap='outerHTML',
        title=title,
        cls=f'editable {cls}',
    )


def _save_cancel_buttons():
    return (
        Button(Icon('check'), type='submit', title='Save (Enter)', cls='btn btn-xs btn-primary btn-square'),
        Button(Icon('xmark'), type='button', title='Cancel (Esc)', onclick='cancelAgendaEdit()', cls='btn btn-xs btn-ghost btn-square'),
    )


def _inline_form(event_id: int, *controls, trigger: str = 'submit', cls: str = ''):
    """Small form that saves one field and re-renders the agenda list"""
    return Form(
        *controls,
        hx_post=f'/admin/agenda/{event_id}/update',
        hx_target='#agenda-list',
        hx_swap='outerHTML',
        hx_trigger=trigger,
        cls=f'inline-editor {cls}',
    )


def agenda_admin_card(event: Event, error: Optional[str] = None) -> Div:
    speakers = event.speakers
    return Div(
        Div(Icon('exclamation-triangle', cls='mr-2'), Span(error), cls='alert alert-error py-2 text-sm') if error else None,
        Div(
            Div(
                Icon('clock', cls='text-primary text-xs mr-1'),
                _editable(event.start_time.strftime('%I:%M %p'), event.id, 'start_time', 'text-sm text-primary font-medium', 'Edit start time'),
                Span('–', cls='mx-1 text-primary'),
                _editable(event.end_time.strftime('%I:%M %p'), event.id, 'end_time', 'text-sm text-primary font-medium', 'Edit end time'),
                cls='flex items-center',
            ),
            _editable(_category_label(event.category), event.id, 'category', 'badge badge-outline badge-primary', 'Change category'),
            cls='flex justify-between items-center gap-2 flex-wrap',
        ),
        H3(_editable(event.title, event.id, 'title', 'text-base font-semibold', 'Edit title')),
        Div(
            Icon('location-dot', cls='mr-2 opacity-60 text-xs'),
            _editable(event.location or 'Add location', event.id, 'location', 'text-sm' + ('' if event.location else ' empty'), 'Edit location'),
            cls='flex items-center',
        ),
        Div(
            Icon('microphone', cls='mr-2 opacity-60 text-xs'),
            _editable(
                Div(
                    *[Span(Img(src=s.image_url, alt='', cls='w-5 h-5 rounded-full object-cover'), s.name, cls='flex items-center gap-1') for s in speakers]
                    or [Span('Add speakers', cls='text-sm')],
                    cls='flex flex-wrap gap-x-3 gap-y-1 text-sm',
                ),
                event.id, 'speakers', '' if speakers else 'empty', 'Edit speakers',
            ),
            cls='flex items-center',
        ),
        P(event.description, cls='text-xs opacity-70 line-clamp-2 whitespace-pre-line') if event.description else None,
        Div(
            Button(
                Icon('align-left', cls='mr-1'), 'Edit description',
                hx_get=f'/admin/agenda/{event.id}/edit/description',
                hx_target='#description-modal-body',
                onclick="document.getElementById('description-modal').showModal()",
                cls='btn btn-xs btn-outline btn-primary',
            ),
            Form(
                Button(Icon('trash', cls='mr-1'), 'Delete', type='submit', cls='btn btn-xs btn-ghost text-error'),
                method='post',
                action=f'/admin/agenda/{event.id}/delete',
                onsubmit=f"return confirm('Delete \"{event.title.replace(chr(39), '').replace(chr(34), '')}\"? Its Q&A questions will be deleted too.')",
            ),
            cls='flex gap-2 justify-end items-center',
        ),
        id=f'event-{event.id}',
        cls='timeline-box p-4 flex flex-col gap-2 bg-base-100',
    )


def agenda_list(events: List[Event], errors: Optional[Dict[int, str]] = None) -> Div:
    errors = errors or {}
    events = sorted(events, key=lambda e: e.start_time)
    return Div(
        Div(
            P(f'{len(events)} session{"s" if len(events) != 1 else ""} · click any field to edit', cls='text-sm opacity-70'),
            A(Icon('plus', cls='mr-1'), 'Add session', href='/admin/agenda/new', cls='btn btn-sm btn-primary'),
            cls='flex justify-between items-center gap-2',
        ),
        *[agenda_admin_card(e, errors.get(e.id)) for e in events],
        id='agenda-list',
        cls='flex flex-col gap-4 p-6',
    )


async def _list_response(errors: Optional[Dict[int, str]] = None) -> Div:
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
    return agenda_list(events, errors)


def _field_editor(event: Event, field: str, all_speakers: List[Speaker]):
    if field in ('title', 'location'):
        return _inline_form(
            event.id,
            Input(name=field, value=getattr(event, field) or '', autofocus=True, required=field == 'title',
                  placeholder=field.title(), cls='input input-bordered input-sm inline-input w-full'),
            *_save_cancel_buttons(),
            cls='flex items-center gap-1 w-full',
        )
    if field in ('start_time', 'end_time'):
        return _inline_form(
            event.id,
            Input(type='time', name=field, value=getattr(event, field).strftime(INPUT_TIME_FORMAT), autofocus=True,
                  required=True, cls='input input-bordered input-sm inline-input'),
            *_save_cancel_buttons(),
            cls='inline-flex items-center gap-1',
        )
    if field == 'category':
        categories = CATEGORIES if event.category in CATEGORIES else [event.category or 'MAIN', *CATEGORIES]
        return _inline_form(
            event.id,
            Select(
                *[Option(_category_label(c), value=c, selected=c == event.category) for c in categories],
                name='category', autofocus=True, cls='select select-bordered select-sm inline-input',
            ),
            Button(Icon('xmark'), type='button', title='Cancel (Esc)', onclick='cancelAgendaEdit()', cls='btn btn-xs btn-ghost btn-square'),
            trigger='change',
            cls='inline-flex items-center gap-1',
        )
    if field == 'speakers':
        selected = {s.id for s in event.speakers}
        return _inline_form(
            event.id,
            Input(type='hidden', name='speakers', value='1'),
            Div(
                *[Label(
                    Input(type='checkbox', name='speaker_ids', value=str(s.id), checked=s.id in selected, cls='checkbox checkbox-xs checkbox-primary'),
                    Img(src=s.image_url, alt='', cls='w-6 h-6 rounded-full object-cover'),
                    Span(s.name, cls='text-sm'),
                    cls='flex items-center gap-2 cursor-pointer py-1',
                ) for s in sorted(all_speakers, key=lambda s: s.name)],
                cls='flex flex-col max-h-56 overflow-y-auto',
            ),
            Div(
                A(Icon('user-plus', cls='mr-1'), 'Add new speaker', href=f'/admin/speakers/new?event_id={event.id}', cls='btn btn-xs btn-ghost text-primary'),
                Div(
                    Button('Cancel', type='button', onclick='cancelAgendaEdit()', cls='btn btn-xs btn-ghost'),
                    Button('Save', type='submit', cls='btn btn-xs btn-primary'),
                    cls='flex gap-1',
                ),
                cls='flex justify-between items-center border-t border-base-300 pt-2 mt-1',
            ),
            cls='w-full border border-base-300 rounded-lg p-2 bg-base-100',
        )
    if field == 'description':
        return _inline_form(
            event.id,
            H3(event.title, cls='font-semibold mb-2'),
            Textarea(event.description or '', name='description', rows=14, autofocus=True,
                     placeholder='Describe this session…',
                     cls='textarea textarea-bordered w-full text-sm leading-relaxed'),
            Div(
                Button('Cancel', type='button', onclick="document.getElementById('description-modal').close()", cls='btn btn-sm btn-ghost'),
                Button(Icon('save', cls='mr-1'), 'Save', type='submit', cls='btn btn-sm btn-primary'),
                cls='modal-action mt-3',
            ),
        )
    return None


def agenda_form(action: str, speakers: List[Speaker], event: Optional[Event] = None,
                values: Optional[dict] = None, error: Optional[str] = None) -> Form:
    """Full add/edit session form. `values` holds submitted data when re-rendering after a validation error."""
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
                *[Option(_category_label(c), value=c, selected=c == values['category']) for c in categories],
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
            A(Icon('user-plus', cls='mr-1'), 'Add new speaker', href='/admin/speakers/new', cls='btn btn-xs btn-ghost text-primary self-start'),
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
    """Read and validate the full session form. Returns (values, error)."""
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


def _page(title: str, content, sess, *extra):
    return AppContainer(
        Div(TopNav(title), content, *extra, id='page-content', cls='blue-background agenda-admin'),
        is_moderator=is_moderator(sess),
    )


@rt('/admin/agenda')
@require_moderator
async def get(req, sess):
    """All sessions as cards; every field is editable in place"""
    return _page(
        'Edit Agenda',
        await _list_response(),
        sess,
        Dialog(
            Div(Div(id='description-modal-body'), cls='modal-box w-11/12 max-w-2xl'),
            Form(Button('close'), method='dialog', cls='modal-backdrop'),
            id='description-modal',
            cls='modal',
        ),
        Style(ADMIN_CSS),
        Script(ADMIN_JS),
    )


@rt('/admin/agenda/list')
@require_moderator
async def get(req, sess):
    return await _list_response()


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


@rt('/admin/agenda/{event_id}/edit/{field}')
@require_moderator
async def get(req, sess, event_id: int, field: str):
    """Inline editor for a single field of a session card"""
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        all_speakers = await get_speakers(db) if field == 'speakers' else []
    editor = _field_editor(event, field, all_speakers) if event else None
    return editor if editor is not None else Response('Not found', status_code=404)


@rt('/admin/agenda/{event_id}/update')
@require_moderator
async def post(req, sess, event_id: int):
    """Save whichever fields were submitted and return the re-rendered list"""
    form = await req.form()
    error = None
    async with db_manager.AsyncSessionLocal() as db:
        # Plain get (no speaker image enrichment) so nothing but the edited fields is written
        event = await db.get(Event, event_id)
        if not event:
            return Response('Session not found', status_code=404)

        changes = {}
        if 'title' in form:
            changes['title'] = form['title'].strip()
            if not changes['title']:
                error = 'Title cannot be empty.'
        if 'location' in form:
            changes['location'] = form['location'].strip() or None
        if 'description' in form:
            changes['description'] = form['description'].strip() or None
        if 'category' in form:
            changes['category'] = form['category']
        if 'speakers' in form:
            changes['speaker_ids'] = [int(i) for i in form.getlist('speaker_ids')]
        for name in ('start_time', 'end_time'):
            if name in form:
                try:
                    t = datetime.strptime(form[name], INPUT_TIME_FORMAT).time()
                    changes[name] = datetime.combine(getattr(event, name).date(), t, tzinfo=timezone.utc)
                except ValueError:
                    error = 'Please enter a valid time.'
        if not error and changes.get('end_time', event.end_time) <= changes.get('start_time', event.start_time):
            error = 'End time must be after start time.'

        if not error:
            await update_event(db, event_id, EventUpdate(**changes))
    return await _list_response({event_id: error} if error else None)


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


def speaker_form(event: Optional[Event], values: dict, error: Optional[str] = None) -> Form:
    def field(label, control):
        return Label(Span(label, cls='label-text font-medium'), control, cls='form-control w-full gap-1')

    return Form(
        Div(Icon('exclamation-triangle', cls='mr-2'), Span(error), cls='alert alert-error') if error else None,
        P('The speaker will be added to: ', Span(event.title, cls='font-semibold'), cls='text-sm') if event else None,
        Input(type='hidden', name='event_id', value=str(event.id) if event else ''),
        field('Name', Input(name='name', value=values.get('name', ''), required=True, autofocus=True,
                            placeholder='e.g. Sh. Yaser Birjas', cls='input input-bordered w-full')),
        field('Photo URL (optional)', Input(name='image_url', value=values.get('image_url', ''), placeholder='https://… or /assets/speaker.png',
                                            cls='input input-bordered w-full')),
        field('Bio', Textarea(values.get('bio', ''), name='bio', rows=6, cls='textarea textarea-bordered w-full')),
        Div(
            A('Cancel', href=f'/admin/agenda#event-{event.id}' if event else '/admin/agenda', cls='btn btn-ghost'),
            Button(Icon('save', cls='mr-1'), 'Add speaker', type='submit', cls='btn btn-primary'),
            cls='flex justify-end gap-2',
        ),
        method='post',
        action='/admin/speakers/new',
        cls='flex flex-col gap-4 p-6 white-background',
    )


@rt('/admin/speakers/new')
@require_moderator
async def get(req, sess, event_id: int = None):
    async with db_manager.AsyncSessionLocal() as db:
        event = await db.get(Event, event_id) if event_id else None
    return _page('Add Speaker', speaker_form(event, {}), sess)


@rt('/admin/speakers/new')
@require_moderator
async def post(req, sess):
    """Create a speaker, optionally attaching them to the session they were added from"""
    form = await req.form()
    values = {k: (form.get(k) or '').strip() for k in ('name', 'image_url', 'bio')}
    event_id = int(form['event_id']) if form.get('event_id') else None
    async with db_manager.AsyncSessionLocal() as db:
        if not values['name']:
            event = await db.get(Event, event_id) if event_id else None
            return _page('Add Speaker', speaker_form(event, values, 'Name is required.'), sess)

        speaker = await create_speaker(db, SpeakerCreate(name=values['name'], image_url=values['image_url'] or None, bio=values['bio'] or None))
        if event_id and await db.get(Event, event_id):
            await db.execute(event_speakers.insert().values(event_id=event_id, speaker_id=speaker.id))
            await db.commit()
    return RedirectResponse(f'/admin/agenda#event-{event_id}' if event_id else '/admin/agenda', status_code=303)

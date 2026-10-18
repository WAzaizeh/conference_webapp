"""Admin pages for speakers and sponsors: text fields plus photo/logo uploads stored in the database
(utils/images.py), so changing an image needs no code push."""
from typing import Optional

from fasthtml.common import RedirectResponse, Script
from fasthtml.components import A, Button, Div, Form, H2, Img, Input, Label, P, Span, Textarea
from sqlalchemy import delete

from components.cards import SponsorLogo
from components.icon import Icon
from components.navigation import TopNav
from components.page import AppContainer
from core.app import rt
from crud.speaker import get_speakers
from crud.sponsor import get_sponsors
from db.connection import db_manager
from db.models import Event, Speaker, Sponsor, event_speakers
from utils.auth import is_moderator, require_admin
from utils.images import prepare_upload, replace_image, save_image
from utils.speaker_utils import speaker_photo

SPONSOR_FIELDS = ('name', 'description', 'website', 'facebook', 'instagram', 'twitter', 'youtube', 'linkedin', 'tiktok', 'snapchat')

# Show the chosen file in place of the current image before saving
PREVIEW_JS = """
document.addEventListener('change', (e) => {
    const input = e.target.closest('input[type=file][data-preview]');
    if (!input || !input.files[0]) return;
    const img = document.getElementById(input.dataset.preview);
    img.src = URL.createObjectURL(input.files[0]);
    img.hidden = false;
    const fallback = document.getElementById(input.dataset.preview + '-fallback');
    if (fallback) fallback.hidden = true;
});
"""


def _page(title: str, content, sess):
    return AppContainer(
        Div(TopNav(title), content, Script(PREVIEW_JS), id='page-content', cls='blue-background'),
        is_moderator=is_moderator(sess),
    )


def _field(label, control):
    return Label(Span(label, cls='label-text font-medium'), control, cls='form-control w-full gap-1')


def _text(name, values, **kwargs):
    return Input(name=name, value=values.get(name) or '', cls='input input-bordered w-full', **kwargs)


def _error(error):
    return Div(Icon('exclamation-triangle', cls='mr-2'), Span(error), cls='alert alert-error') if error else None


def _image_field(label: str, current, help_text: str, has_upload: bool):
    """Current image (or fallback) with a file picker; `current` is an Img or fallback element"""
    return _field(label, Div(
        current,
        Div(
            Input(type='file', name='image', accept='image/*', data_preview='image-preview',
                  cls='file-input file-input-bordered file-input-sm w-full'),
            P(help_text, cls='text-xs opacity-70'),
            Label(Input(type='checkbox', name='remove_image', cls='checkbox checkbox-xs'),
                  Span('Remove current image', cls='text-sm'), cls='flex items-center gap-2 cursor-pointer')
            if has_upload else None,
            cls='flex flex-col gap-2 flex-1',
        ),
        cls='flex items-start gap-4',
    ))


def _buttons(cancel_href: str, submit_label: str, delete_action: Optional[str] = None, delete_what: str = ''):
    return Div(
        Button(Icon('trash', cls='mr-1'), 'Delete', type='submit', formaction=delete_action, formnovalidate=True,
               onclick=f"return confirm('Delete {delete_what}? This cannot be undone.')",
               cls='btn btn-ghost text-error mr-auto') if delete_action else None,
        A('Cancel', href=cancel_href, cls='btn btn-ghost'),
        Button(Icon('save', cls='mr-1'), submit_label, type='submit', cls='btn btn-primary'),
        cls='flex justify-end gap-2',
    )


def _form(action: str, *children):
    return Form(*children, method='post', action=action, enctype='multipart/form-data',
                cls='flex flex-col gap-4 p-6 white-background')


async def _read_image(form, kind: str):
    """What the form asks for the image: None (keep), 'remove', or prepared (data, content_type).
    Raises ValueError for a bad file, before anything is written."""
    upload = form.get('image')
    if upload is not None and getattr(upload, 'filename', ''):
        return prepare_upload(await upload.read(), kind)
    return 'remove' if form.get('remove_image') else None


async def _apply_image(db, record, image):
    """Carry out what _read_image returned"""
    if image == 'remove':
        await replace_image(db, record, None)
    elif image:
        await replace_image(db, record, await save_image(db, *image))


def _list_row(href: str, image, name: str, detail: str = ''):
    return A(
        image,
        Div(H2(name, cls='font-medium'), P(detail, cls='text-xs opacity-70') if detail else None, cls='flex-1'),
        Icon('pen', cls='opacity-60'),
        href=href,
        cls='flex items-center gap-3 p-3 white-background rounded-lg',
    )


def _switcher(active: str):
    return Div(
        *[A(label, href=href, cls=f"btn btn-sm {'btn-primary' if key == active else 'btn-ghost'}")
          for key, label, href in (('speakers', 'Speakers', '/admin/speakers'), ('sponsors', 'Sponsors', '/admin/sponsors'))],
        cls='flex justify-center gap-2',
    )


# ---- Speakers ----

def speaker_form(action: str, values: dict, speaker: Optional[Speaker] = None, event: Optional[Event] = None,
                 error: Optional[str] = None):
    cancel = f'/admin/agenda#event-{event.id}' if event else '/admin/speakers'
    preview = Img(src=speaker_photo(speaker) if speaker else '', id='image-preview', alt='',
                  hidden=not speaker, cls='w-24 h-24 rounded-full object-cover shrink-0')
    return _form(
        action,
        _error(error),
        P('The speaker will be added to: ', Span(event.title, cls='font-semibold'), cls='text-sm') if event else None,
        Input(type='hidden', name='event_id', value=str(event.id) if event else ''),
        _field('Name', _text('name', values, required=True, autofocus=not speaker, placeholder='e.g. Sh. Yaser Birjas')),
        _image_field('Photo', preview, 'Cropped to a centred square. JPEG, PNG or WebP.',
                     has_upload=bool(speaker and speaker.image_url)),
        _field('Bio', Textarea(values.get('bio') or '', name='bio', rows=8, cls='textarea textarea-bordered w-full')),
        _buttons(cancel, 'Save' if speaker else 'Add speaker',
                 f'/admin/speakers/{speaker.id}/delete' if speaker else None, 'this speaker'),
    )


@rt('/admin/speakers')
@require_admin
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db:
        speakers = await get_speakers(db)
    return _page('Edit Speakers', Div(
        _switcher('speakers'),
        *[_list_row(f'/admin/speakers/{s.id}', Img(src=speaker_photo(s), alt='', cls='w-12 h-12 rounded-full object-cover'),
                    s.name, 'No bio yet' if not s.bio else '') for s in speakers],
        A(Icon('user-plus', cls='mr-1'), 'Add speaker', href='/admin/speakers/new', cls='btn btn-primary self-center'),
        cls='flex flex-col gap-3 p-4',
    ), sess)


@rt('/admin/speakers/new')
@require_admin
async def get(req, sess, event_id: int = None):
    async with db_manager.AsyncSessionLocal() as db:
        event = await db.get(Event, event_id) if event_id else None
    return _page('Add Speaker', speaker_form('/admin/speakers/new', {}, event=event), sess)


@rt('/admin/speakers/new')
@require_admin
async def post(req, sess):
    """Create a speaker, optionally attaching them to the session they were added from"""
    form = await req.form()
    values = {k: (form.get(k) or '').strip() for k in ('name', 'bio')}
    event_id = int(form['event_id']) if form.get('event_id') else None
    async with db_manager.AsyncSessionLocal() as db:
        event = await db.get(Event, event_id) if event_id else None
        image, error = None, None if values['name'] else 'Name is required.'
        if not error:
            try:
                image = await _read_image(form, 'photo')
            except ValueError as e:
                error = str(e)
        if error:
            return _page('Add Speaker', speaker_form('/admin/speakers/new', values, event=event, error=error), sess)
        speaker = Speaker(name=values['name'], bio=values['bio'] or None)
        await _apply_image(db, speaker, image)
        db.add(speaker)
        await db.flush()
        if event:
            await db.execute(event_speakers.insert().values(event_id=event.id, speaker_id=speaker.id))
        await db.commit()
    return RedirectResponse(f'/admin/agenda#event-{event_id}' if event_id else '/admin/speakers', status_code=303)


@rt('/admin/speakers/{speaker_id}')
@require_admin
async def get(req, sess, speaker_id: int):
    async with db_manager.AsyncSessionLocal() as db:
        speaker = await db.get(Speaker, speaker_id)
    if not speaker:
        return RedirectResponse('/admin/speakers', status_code=303)
    return _page('Edit Speaker', speaker_form(f'/admin/speakers/{speaker_id}', vars(speaker), speaker), sess)


@rt('/admin/speakers/{speaker_id}')
@require_admin
async def post(req, sess, speaker_id: int):
    form = await req.form()
    values = {k: (form.get(k) or '').strip() for k in ('name', 'bio')}
    async with db_manager.AsyncSessionLocal() as db:
        speaker = await db.get(Speaker, speaker_id)
        if not speaker:
            return RedirectResponse('/admin/speakers', status_code=303)
        image, error = None, None if values['name'] else 'Name is required.'
        if not error:
            try:
                image = await _read_image(form, 'photo')
            except ValueError as e:
                error = str(e)
        if error:
            return _page('Edit Speaker', speaker_form(f'/admin/speakers/{speaker_id}', values, speaker, error=error), sess)
        await _apply_image(db, speaker, image)
        speaker.name, speaker.bio = values['name'], values['bio'] or None
        await db.commit()
    return RedirectResponse('/admin/speakers', status_code=303)


@rt('/admin/speakers/{speaker_id}/delete')
@require_admin
async def post(req, sess, speaker_id: int):
    """Delete a speaker and their photo; their sessions stay, without them"""
    async with db_manager.AsyncSessionLocal() as db:
        speaker = await db.get(Speaker, speaker_id)
        if speaker:
            await db.execute(delete(event_speakers).where(event_speakers.c.speaker_id == speaker_id))
            await replace_image(db, speaker, None)
            await db.delete(speaker)
            await db.commit()
    return RedirectResponse('/admin/speakers', status_code=303)


# ---- Sponsors ----

def sponsor_form(action: str, values: dict, sponsor: Optional[Sponsor] = None, error: Optional[str] = None):
    logo = SponsorLogo(sponsor, size='sm') if sponsor else None
    preview = Div(
        Img(src='', id='image-preview', alt='', hidden=True, cls='w-full h-full object-contain'),
        Div(logo, id='image-preview-fallback') if logo else None,
        cls='w-28 h-20 flex items-center justify-center shrink-0',
    )
    return _form(
        action,
        _error(error),
        _field('Name', _text('name', values, required=True, autofocus=not sponsor)),
        _image_field('Logo', preview, 'Any shape; shown scaled to fit. PNG with a transparent background works best.',
                     has_upload=bool(sponsor and sponsor.image_url)),
        _field('Description', Textarea(values.get('description') or '', name='description', rows=4,
                                       cls='textarea textarea-bordered w-full')),
        _field('Website', _text('website', values, type='url', placeholder='https://…')),
        _field('Facebook', _text('facebook', values, type='url', placeholder='https://facebook.com/…')),
        _field('Instagram', _text('instagram', values, type='url', placeholder='https://instagram.com/…')),
        _field('X / Twitter', _text('twitter', values, type='url', placeholder='https://x.com/…')),
        _field('YouTube', _text('youtube', values, type='url', placeholder='https://youtube.com/…')),
        _field('LinkedIn', _text('linkedin', values, type='url', placeholder='https://linkedin.com/company/…')),
        _field('TikTok', _text('tiktok', values, type='url', placeholder='https://tiktok.com/@…')),
        _field('Snapchat', _text('snapchat', values, type='url', placeholder='https://snapchat.com/@…')),
        _buttons('/admin/sponsors', 'Save' if sponsor else 'Add sponsor',
                 f'/admin/sponsors/{sponsor.id}/delete' if sponsor else None, 'this sponsor'),
    )


def _sponsor_values(form) -> dict:
    return {k: (form.get(k) or '').strip() for k in SPONSOR_FIELDS}


async def _save_sponsor(db, sponsor: Sponsor, form, values: dict) -> Optional[str]:
    """Apply the form to the sponsor; returns an error message instead when it can't be saved"""
    if not values['name']:
        return 'Name is required.'
    try:
        image = await _read_image(form, 'logo')
    except ValueError as e:
        return str(e)
    await _apply_image(db, sponsor, image)
    for k, v in values.items():
        setattr(sponsor, k, v or None)
    return None


@rt('/admin/sponsors')
@require_admin
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db:
        sponsors = await get_sponsors(db)
    return _page('Edit Sponsors', Div(
        _switcher('sponsors'),
        *[_list_row(f'/admin/sponsors/{s.id}', SponsorLogo(s), s.name) for s in sponsors],
        A(Icon('plus', cls='mr-1'), 'Add sponsor', href='/admin/sponsors/new', cls='btn btn-primary self-center'),
        cls='flex flex-col gap-3 p-4',
    ), sess)


@rt('/admin/sponsors/new')
@require_admin
async def get(req, sess):
    return _page('Add Sponsor', sponsor_form('/admin/sponsors/new', {}), sess)


@rt('/admin/sponsors/new')
@require_admin
async def post(req, sess):
    form = await req.form()
    values = _sponsor_values(form)
    async with db_manager.AsyncSessionLocal() as db:
        sponsor = Sponsor()
        error = await _save_sponsor(db, sponsor, form, values)
        if error:
            return _page('Add Sponsor', sponsor_form('/admin/sponsors/new', values, error=error), sess)
        db.add(sponsor)
        await db.commit()
    return RedirectResponse('/admin/sponsors', status_code=303)


@rt('/admin/sponsors/{sponsor_id}')
@require_admin
async def get(req, sess, sponsor_id: int):
    async with db_manager.AsyncSessionLocal() as db:
        sponsor = await db.get(Sponsor, sponsor_id)
    if not sponsor:
        return RedirectResponse('/admin/sponsors', status_code=303)
    return _page('Edit Sponsor', sponsor_form(f'/admin/sponsors/{sponsor_id}', vars(sponsor), sponsor), sess)


@rt('/admin/sponsors/{sponsor_id}')
@require_admin
async def post(req, sess, sponsor_id: int):
    form = await req.form()
    values = _sponsor_values(form)
    async with db_manager.AsyncSessionLocal() as db:
        sponsor = await db.get(Sponsor, sponsor_id)
        if not sponsor:
            return RedirectResponse('/admin/sponsors', status_code=303)
        error = await _save_sponsor(db, sponsor, form, values)
        if error:
            return _page('Edit Sponsor', sponsor_form(f'/admin/sponsors/{sponsor_id}', values, sponsor, error=error), sess)
        await db.commit()
    return RedirectResponse('/admin/sponsors', status_code=303)


@rt('/admin/sponsors/{sponsor_id}/delete')
@require_admin
async def post(req, sess, sponsor_id: int):
    async with db_manager.AsyncSessionLocal() as db:
        sponsor = await db.get(Sponsor, sponsor_id)
        if sponsor:
            await replace_image(db, sponsor, None)
            await db.delete(sponsor)
            await db.commit()
    return RedirectResponse('/admin/sponsors', status_code=303)

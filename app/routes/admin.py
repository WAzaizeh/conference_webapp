from components.icon import Icon
from components.page import AppContainer
from fasthtml.common import RedirectResponse, Response
from fasthtml.components import Button, H1, Div, Form, Label, Input, Span
from core.app import rt
from utils.auth import verify_password, require_moderator, get_user_by_email, is_moderator
from db.connection import db_manager

@rt('/settings')
def get_settings(sess):
    # Buttons for settings options
    general_btn = Button('General Settings', disabled=True, cls='btn btn-block btn-glass')
    privacy_btn = Button('Privacy', disabled=True, cls='btn btn-block btn-glass')
    notifications_btn = Button('Notifications', disabled=True, cls='btn btn-block btn-glass')
    admin_access_btn = Button(
        'Admin Access',
        hx_get='/admin_login',
        hx_target='#page-content',
        hx_swap='outerHTML',
        id='admin-access-btn',
        cls='btn btn-block btn-glass'
    )

    # Layout for the settings page
    content = [
        H1('Settings', cls='text-2xl font-bold mb-6 text-center'),
        general_btn,
        privacy_btn,
        notifications_btn,
        admin_access_btn
    ]
    return AppContainer(
        Div(
            *content,
            id='page-content',
            cls='flex flex-col items-center justify-evenly blue-background'
        ),
        is_moderator=is_moderator(sess)
    )

@rt('/admin/login')
async def post(request, sess, username: str, password: str):
    """Handle login form submission from modal"""
    async with db_manager.AsyncSessionLocal() as db:
        user = await get_user_by_email(db, username)
        
        if user and verify_password(password, user.password_hash):
            # Set session
            sess['user_id'] = str(user.id)
            sess['admin_auth'] = True
            
            # Close modal and refresh page
            return Response(
                headers={
                    'HX-Refresh': 'true'  # Tell HTMX to refresh the page
                }
            )
        else:
            # Return error message to display in modal
            return Div(
                Div(
                    Icon('exclamation-triangle', cls='text-error text-xl mr-2'),
                    Span("Invalid username or password", cls="font-semibold"),
                    cls="alert alert-error mb-4 flex items-center"
                )
            )

@rt('/admin/logout')
def get(sess):
    """Logout and clear only admin session"""
    # Only clear admin-related session keys
    sess.pop('admin_auth', None)
    sess.pop('user_id', None)
    return RedirectResponse('/', status_code=303)

@rt('/admin_login') 
def get(sess):
    """Direct access login page"""
    return AppContainer(
        Div(
            H1('Admin Login', cls='text-2xl font-bold mb-6 text-center'),
            Form(
                Label(
                    Icon('user', cls='h-4 w-4 opacity-70'),
                    Input(placeholder='Username', name='username', type='text', cls='grow', required=True),
                    cls='input input-bordered flex items-center gap-2',
                ),
                Label(
                    Icon('key', cls='h-4 w-4 opacity-70'),
                    Input(placeholder='Password', name='password', type='password', cls='grow', required=True),
                    cls='input input-bordered flex items-center gap-2',
                ),
                Button('Login', type='submit', cls='btn btn-primary'),
                hx_post='/admin/login',
                method='post',
                cls='flex flex-col items-center justify-evenly h-35-vh',
            ),
            id='page-content',
            cls='flex flex-col items-center justify-start blue-background'
        ),
        is_moderator=False
    )

@rt('/admin_dashboard')
@require_moderator
def get(req, sess):
    """Admin dashboard - requires moderator authentication"""

    # Create buttons for each edit option
    moderate_qa_btn = Button(
        Icon('forum'),
        ' Moderate Q&A',
        onclick="window.location.href='/qa/moderator'",
        id='moderate-qa-btn',
        cls='btn btn-block btn-glass btn-primary'
    )
    moderate_feedback_btn = Button(
        Icon('poll'),
        ' Moderate Feedback',
        onclick="window.location.href='/feedback/moderator'",
        id='moderate-feedback-btn',
        cls='btn btn-block btn-glass btn-primary'
    )
    edit_speakers_btn = Button('Edit Speakers', hx_get='/edit-speakers', id='edit-speakers-btn', cls='btn btn-block btn-glass')
    edit_events_btn = Button('Edit Events', hx_get='/edit-events', id='edit-events-btn', cls='btn btn-block btn-glass')
    edit_prayer_times_btn = Button('Edit Prayer Times', hx_get='/edit-prayer-times', id='edit-prayer-times-btn', cls='btn btn-block btn-glass')
    edit_sponsors_btn = Button('Edit Sponsors', hx_get='/edit-sponsors', id='edit-sponsors-btn', cls='btn btn-block btn-glass')
    edit_registration_link_btn = Button('Edit Registration Link', hx_get='/edit-registration-link', id='edit-registration-link-btn', cls='btn btn-block btn-glass')

    # Layout for the admin dashboard
    content = [
        H1('Admin Dashboard', cls='text-2xl font-bold mb-6 text-center'),
        moderate_qa_btn,
        moderate_feedback_btn,
        edit_speakers_btn,
        edit_events_btn,
        edit_prayer_times_btn,
        edit_sponsors_btn,
        edit_registration_link_btn,
    ]

    return AppContainer(
        Div(
            *content,
            id='page-content',
            cls='flex flex-col items-center justify-evenly blue-background h-70-vh'
        ),
        is_moderator=is_moderator(sess)
    )

@rt('/logout')
def get(sess):
    """Logout route - alias for /admin/logout"""
    # Only clear admin-related session keys
    sess.pop('admin_auth', None)
    sess.pop('user_id', None)
    return RedirectResponse('/', status_code=303)
import os
from dotenv import load_dotenv
from hmac import compare_digest
from dataclasses import dataclass
from components.icon import Icon
from components.page import AppContainer
from fasthtml.common import Router, RedirectResponse
from fasthtml.components import Button, H1, Div, Form, Label, Input


def get_admin_routes(rt: Router):
    @rt('/settings')
    def get_settings():
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
                        )
                    )

    @rt('/admin_login') 
    def get():
        return AppContainer(
                Div(
                    H1('Admin Login', cls='text-2xl font-bold mb-6 text-center'),
                    Form(
                        Label(
                            Icon('user', cls='h-4 w-4 opacity-70'),
                            Input(placeholder='Username', name='username', type='text', cls='grow'),
                            cls='input input-bordered flex items-center gap-2',
                            ),
                        Label(
                            Icon('key', cls='h-4 w-4 opacity-70'),
                            Input(placeholder='Password', name='password', type='password', cls='grow'),
                            cls='input input-bordered flex items-center gap-2',
                            ),
                        Button('Login', cls='btn btn-primary'),
                        hx_post='/admin_login',
                        method='post',
                        cls='flex flex-col items-center justify-evenly h-35-vh',
                    ),
                    id='page-content',
                    cls='flex flex-col items-center justify-start blue-background'
                )
            )

    # Handling admin login POST request
    load_dotenv()
    @dataclass
    class AdminLogin: username: str; password: str

    @rt('/admin_login')
    def post(admin: AdminLogin, sess):
        # Get admin credentials from environment variables
        ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
        print(ADMIN_USERNAME)
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

        if not admin.username or not admin.password:
            return RedirectResponse('/admin_login', status_code=303)
        
        # Compare preset credentials with input
        if compare_digest(admin.username, ADMIN_USERNAME) and compare_digest(admin.password, ADMIN_PASSWORD):
            sess['admin_auth'] = True
            return RedirectResponse('/admin_dashboard', status_code=303)
        else:
            return RedirectResponse('/admin_login', status_code=303)

    @rt('/admin_dashboard')
    def get(sess):
        # Ensure the user is authenticated as admin
        if not sess.get('admin_auth', False):
            return RedirectResponse('/admin_login', status_code=303)

        # Create buttons for each edit option
        edit_speakers_btn = Button('Edit Speakers', hx_get='/edit-speakers', id='edit-speakers-btn', cls='btn btn-block btn-glass')
        edit_events_btn = Button('Edit Events', hx_get='/edit-events', id='edit-events-btn', cls='btn btn-block btn-glass')
        edit_prayer_times_btn = Button('Edit Prayer Times', hx_get='/edit-prayer-times', id='edit-prayer-times-btn', cls='btn btn-block btn-glass')
        edit_sponsors_btn = Button('Edit Sponsors', hx_get='/edit-sponsors', id='edit-sponsors-btn', cls='btn btn-block btn-glass')
        edit_registration_link_btn = Button('Edit Registration Link', hx_get='/edit-registration-link', id='edit-registration-link-btn', cls='btn btn-block btn-glass')
        edit_feedback_survey_link_btn = Button('Edit Feedback Survey Link', hx_get='/edit-feedback-survey', id='edit-feedback-survey-btn', cls='btn btn-block btn-glass')

        # Layout for the admin dashboard
        content = [
            H1('Admin Dashboard', cls='text-2xl font-bold mb-6 text-center'),
            edit_speakers_btn,
            edit_events_btn,
            edit_prayer_times_btn,
            edit_sponsors_btn,
            edit_registration_link_btn,
            edit_feedback_survey_link_btn
        ]

        return AppContainer(
                Div(
                *content,
                id='page-content',
                cls='flex flex-col items-center justify-evenly blue-background h-70-vh'
                )
            )
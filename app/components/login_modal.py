from fasthtml.components import Div, Dialog, Form, Button, Label, Input, H3
from .icon import Icon

def LoginModal():
    """Login modal dialog - responsive (bottom on mobile, center on desktop)"""
    return Dialog(
        Div(
            # Close button in top-right corner
            Form(
                Button(
                    Icon('times'),
                    cls="btn btn-sm btn-circle btn-ghost absolute right-2 top-2",
                    formmethod="dialog"
                ),
                method="dialog"
            ),
            
            # Modal content container with height control
            Div(
                # Modal content
                H3("Admin Login", cls="font-bold text-lg mb-4"),
                
                # Login form
                Form(
                    Label(
                        Icon('user', cls='h-4 w-4 opacity-70'),
                        Input(
                            placeholder='Username', 
                            name='username', 
                            type='text', 
                            cls='grow',
                            required=True
                        ),
                        cls='input input-bordered flex items-center gap-2 mb-3',
                    ),
                    Label(
                        Icon('key', cls='h-4 w-4 opacity-70'),
                        Input(
                            placeholder='Password', 
                            name='password', 
                            type='password', 
                            cls='grow',
                            required=True
                        ),
                        cls='input input-bordered flex items-center gap-2 mb-4',
                    ),
                    Div(
                        id='login-error-container'  # Error messages will appear here
                    ),
                    Button('Login', type='submit', cls='btn btn-primary w-full'),
                    hx_post='/admin/login',
                    hx_target='#login-error-container',
                    hx_swap='innerHTML',
                    id='login-form',
                    cls='flex flex-col',
                ),
                cls='flex flex-col justify-evenly h-[40vh]'  # Content spread over 40vh
            ),
            
            cls="modal-box h-[75vh]"  # Modal box height 75vh
        ),
        # Backdrop (click outside to close)
        Form(
            cls="modal-backdrop",
            method="dialog",
            children=[
                Button(type="submit", cls="cursor-default w-full h-full")
            ]
        ),
        id="login-modal",
        cls="modal modal-bottom sm:modal-middle"  # Bottom on mobile, middle on desktop
    )
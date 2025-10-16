from fasthtml.components import Div, Dialog, Form, Button, Label, Input, H3
from .icon import Icon

def LoginModal():
    """Login modal dialog - responsive (bottom on mobile, center on desktop)"""
    btnclass = "btn btn-primary px-6 py-2"
    btnstyle = "background-color: var(--primary-color); border-color: var(--primary-color); color: white;"
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
                H3("Moderator Sign in", cls="text-lg text-semibold text-center mb-4"),
                
                # Login form
                Form(
                    Div(
                        Input(
                            placeholder='Username', 
                            name='username', 
                            type='text', 
                            cls='input input-bordered rounded-sm w-full',
                            required=True
                        ),
                        Input(
                            placeholder='Password', 
                            name='password', 
                            type='password', 
                            cls='input input-bordered rounded-sm w-full',
                            required=True
                        ),
                        cls='form-control gap-4 mb-4',
                    ),
                    Div(
                        id='login-error-container'  # Error messages will appear here
                    ),
                    Button('Sign in', type='submit', cls=btnclass, style=btnstyle,),
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
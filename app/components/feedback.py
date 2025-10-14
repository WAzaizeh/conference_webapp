from fasthtml.common import *

def SingleSelectQuestion(question: str, name: str, options: list[str], required: bool = True, selected_value: str = None):
    """
    Single select radio button question using DaisyUI
    
    Args:
        question: The question text
        name: The form field name
        options: List of option strings
        required: Whether the question is required
        selected_value: The currently selected value (for editing)
    """
    return Div(
        H3(question, cls="text-lg font-semibold mb-3"),
        Div(
            *[
                Label(
                    Input(
                        type="radio",
                        name=name,
                        value=option,
                        cls="radio radio-primary",
                        required=required if i == 0 else False,
                        checked=(option == selected_value)
                    ),
                    Span(option, cls="ml-3"),
                    cls="label cursor-pointer justify-start gap-2 py-2"
                )
                for i, option in enumerate(options)
            ],
            cls="form-control"
        ),
        cls="card bg-base-100 shadow-md p-6 mb-4"
    )


def MultiSelectQuestion(question: str, name: str, options: list[str], required: bool = False, selected_values: list[str] = None):
    """
    Multi select checkbox question using DaisyUI
    
    Args:
        question: The question text
        name: The form field name (will be appended with [] for each option)
        options: List of option strings
        required: Whether at least one option is required
        selected_values: List of currently selected values (for editing)
    """
    if selected_values is None:
        selected_values = []
    
    return Div(
        H3(question, cls="text-lg font-semibold mb-3"),
        Div(
            *[
                Label(
                    Input(
                        type="checkbox",
                        name=f"{name}[]",
                        value=option,
                        cls="checkbox checkbox-primary",
                        checked=(option in selected_values)
                    ),
                    Span(option, cls="ml-3"),
                    cls="label cursor-pointer justify-start gap-2 py-2"
                )
                for option in options
            ],
            cls="form-control"
        ),
        cls="card bg-base-100 shadow-md p-6 mb-4"
    )


def TextInputQuestion(question: str, name: str, placeholder: str = "", required: bool = False, multiline: bool = False, value: str = ""):
    """
    Text input question using DaisyUI
    
    Args:
        question: The question text
        name: The form field name
        placeholder: Placeholder text
        required: Whether the question is required
        multiline: If True, uses textarea instead of input
        value: Pre-filled value (for editing)
    """
    input_field = (
        Textarea(
            value,
            name=name,
            placeholder=placeholder,
            cls="textarea textarea-bordered textarea-primary w-full h-32",
            required=required
        ) if multiline else
        Input(
            type="text",
            name=name,
            value=value,
            placeholder=placeholder,
            cls="input input-bordered input-primary w-full",
            required=required
        )
    )
    
    return Div(
        H3(question, cls="text-lg font-semibold mb-3"),
        Div(
            input_field,
            cls="form-control"
        ),
        cls="card bg-base-100 shadow-md p-6 mb-4"
    )


def RatingQuestion(question: str, name: str, max_rating: int = 5, required: bool = True, selected_rating: str = None):
    """
    Rating question using DaisyUI radio buttons styled as stars
    
    Args:
        question: The question text
        name: The form field name
        max_rating: Maximum rating value (default 5)
        required: Whether the question is required
        selected_rating: The currently selected rating (for editing)
    """
    return Div(
        H3(question, cls="text-lg font-semibold mb-3"),
        Div(
            Div(
                *[
                    Input(
                        type="radio",
                        name=name,
                        value=str(i),
                        cls="mask mask-star",
                        required=required if i == 1 else False,
                        checked="checked" if str(i) == selected_rating else None
                    )
                    for i in range(1, max_rating + 1)
                ],
                cls="rating"
            ),
            cls="form-control"
        ),
        cls="card bg-base-100 shadow-md p-6 mb-4"
    )

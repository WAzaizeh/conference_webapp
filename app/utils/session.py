import uuid


def get_or_create_session_id(request):
    """Get existing session ID from cookie or create new one"""
    session_id = request.cookies.get('qa_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id
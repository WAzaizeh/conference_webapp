def get_speaker_image_url(speaker_id: int, name: str, image_url: str = None) -> str:
    """
    Get the appropriate image URL for a speaker.
    Returns the speaker's image URL if available, otherwise returns placeholder URL.
    
    Args:
        speaker_id: The ID of the speaker
        name: The speaker's name (for generating initials)
        image_url: The speaker's image URL from database (can be None or empty)
        
    Returns:
        str: URL to display for the speaker (either their image or placeholder)
    """
    if image_url and image_url.strip() and image_url != 'null':
        # Return existing image URL - ensure it's absolute
        if image_url.startswith('http://') or image_url.startswith('https://'):
            # External URL, return as-is
            return image_url
        elif image_url.startswith('/'):
            # Already absolute path
            return image_url
        else:
            # Relative path, make it absolute
            return f'/{image_url}'
    
    # Colors from main.css
    AVATAR_COLORS = [
        '004EA3',  # primary-color (blue) - without #
        '009688',  # teal
        '012B59',  # dark blue
        '8395b5',  # light blue-gray
        'A5C7F3',  # light blue
        'C7C7CC',  # secondary-color (gray)
    ]
    
    # Get initials
    parts = name.strip().split()
    if len(parts) >= 2:
        initials = f"{parts[0][0]}{parts[-1][0]}".upper()
    else:
        initials = name[0].upper() if name else "?"
    
    # Pick consistent color based on speaker_id
    bg_color = AVATAR_COLORS[speaker_id % len(AVATAR_COLORS)]
    
    # Generate UI Avatars URL
    # Parameters: name, size, background, color, font-size, rounded, bold
    placeholder_url = (
        f"https://ui-avatars.com/api/"
        f"?name={initials}"
        f"&size=400"
        f"&background={bg_color}"
        f"&color=ffffff"
        f"&font-size=0.5"
        f"&rounded=true"
        f"&bold=true"
    )
    
    return placeholder_url
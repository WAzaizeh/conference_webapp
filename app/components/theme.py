"""Shared look for the 2026 "Him & Her" pages: fonts, parchment colors, paper grain and entrance animations."""
from fasthtml.common import Span

FONTS_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;600&display=swap');"

# Parchment grain, generated in-browser so no extra image asset is needed
NOISE = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .45 0 0 0 0 .30 0 0 0 0 .12 0 0 0 .5 0'/></filter>"
    "<rect width='100%' height='100%' filter='url(%23n)'/></svg>"
)

TOKENS = """
    --cs-navy: #1c3765;
    --cs-navy-deep: #12264a;
    --cs-sand: #e8d6b1;
    --cs-tan: #c9a874;
    --cs-umber: #4f3519;
"""

KEYFRAMES = """
@keyframes cs-rise {
    to { opacity: 1; transform: translateY(0); }
}
@keyframes cs-fade-down {
    from { opacity: 0; transform: translateY(-12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes cs-fade-up {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
"""


def title_letters(text: str, start_delay: float = .55, step: float = .09):
    """Split a headline into individually animated characters (pair with the `cs-rise` keyframes)"""
    letters = []
    for i, ch in enumerate(text):
        if ch == ' ':
            continue
        letters.append(Span(
            ch,
            cls='ch amp' if ch == '&' else 'ch',
            style=f'animation-delay: {start_delay + i * step:.2f}s',
        ))
    return letters

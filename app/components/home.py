from fasthtml.common import A, Div, H1, Img, P, Span, Style
from components.icon import Icon
from components.theme import FONTS_IMPORT, KEYFRAMES, NOISE, TOKENS, title_letters

VENUE_MAP_URL = 'https://www.google.com/maps/search/?api=1&query=GEM+Academy+6300+Independence+Pkwy+Plano+TX+75023'

_CSS = """
__FONTS__

#page-content.home-26 {
__TOKENS__
    color: var(--cs-navy);
    font-family: 'Oswald', sans-serif;
    background:
        url("__NOISE__"),
        radial-gradient(ellipse at 50% 22%, rgba(246, 234, 207, .95) 0%, rgba(232, 214, 177, .55) 40%, transparent 72%),
        radial-gradient(ellipse at 10% 95%, rgba(107, 77, 43, .40), transparent 55%),
        radial-gradient(ellipse at 95% 5%, rgba(107, 77, 43, .30), transparent 50%),
        linear-gradient(165deg, #d8bf92 0%, #c9a874 50%, #b28c58 100%);
    background-blend-mode: multiply, normal, normal, normal, normal;
    box-shadow: inset 0 0 120px 20px rgba(70, 48, 22, .35);
}

.home-inner {
    max-width: 560px;
    margin: 0 auto;
    padding: 64px 20px 32px;
}

.home-header { text-align: center; }

.home-brand {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: .28em;
    text-transform: uppercase;
    color: var(--cs-navy-deep);
    opacity: 0;
    animation: cs-fade-down .8s ease-out .1s forwards;
}
.home-brand img { width: 40px; height: 40px; }

.home-eyebrow {
    margin-top: 22px;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--cs-navy-deep);
    opacity: 0;
    animation: cs-fade-down .8s ease-out .25s forwards;
}

.home-title {
    font-family: 'Anton', 'Oswald', sans-serif;
    font-weight: 400;
    font-size: clamp(72px, 24vw, 132px);
    line-height: .9;
    margin: 4px 0 2px;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    white-space: nowrap;
    color: var(--cs-navy);
    text-shadow: 0 2px 0 rgba(255, 245, 225, .25), 0 10px 30px rgba(60, 40, 15, .25);
}
.home-title .ch {
    display: inline-block;
    opacity: 0;
    transform: translateY(60%);
    animation: cs-rise .7s cubic-bezier(.2, .8, .2, 1) forwards;
}
.home-title .amp { font-size: .62em; margin: 0 -.04em .06em; }

.home-tagline {
    font-weight: 600;
    font-size: clamp(15px, 4.2vw, 20px);
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--cs-navy-deep);
    opacity: 0;
    animation: cs-fade-up .8s ease-out 1.1s forwards;
}

.home-info {
    margin: 22px auto 0;
    padding: 12px 0;
    border-top: 2px solid var(--cs-navy);
    border-bottom: 2px solid var(--cs-navy);
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 6px 18px;
    font-size: 14px;
    letter-spacing: .04em;
    text-transform: uppercase;
    opacity: 0;
    animation: cs-fade-up .8s ease-out 1.3s forwards;
}
.home-info a, .home-info span { display: inline-flex; align-items: center; gap: 8px; }
.home-info a:hover { text-decoration: underline; }
.home-info .date { font-family: 'Anton', 'Oswald', sans-serif; letter-spacing: .05em; }

.home-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-top: 28px;
}

.home-26 .custom-card {
    background: rgba(255, 248, 234, .55);
    border: 1px solid rgba(28, 55, 101, .22);
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(70, 48, 22, .15);
    backdrop-filter: blur(2px);
    padding: 18px 12px;
    gap: 10px;
    justify-content: center;
    transition: transform .2s, background-color .2s, box-shadow .2s;
    opacity: 0;
    animation: cs-fade-up .7s ease-out forwards;
}
.home-26 .custom-card:hover {
    transform: translateY(-2px);
    background: rgba(255, 250, 240, .8);
    box-shadow: 0 10px 24px rgba(70, 48, 22, .22);
}
.home-26 .custom-card p {
    font-family: 'Oswald', sans-serif;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--cs-navy);
    text-align: center;
}
.home-26 .custom-card img { width: 40px; height: 40px; }
.home-26 .custom-card.border-2 { border: 2px solid var(--cs-navy); }
.home-26 .custom-card.home-register {
    grid-column: 1 / -1;
    flex-direction: row;
    gap: 14px;
    background: var(--cs-navy);
    border-color: var(--cs-navy);
}
.home-26 .custom-card.home-register:hover { background: var(--cs-navy-deep); }
.home-26 .custom-card.home-register p { color: #f6ead0; font-size: 16px; }
.home-26 .custom-card.home-register img { filter: brightness(0) invert(.93) sepia(.3); width: 32px; height: 32px; }

.home-grid > :nth-child(1) { animation-delay: 1.45s; }
.home-grid > :nth-child(2) { animation-delay: 1.55s; }
.home-grid > :nth-child(3) { animation-delay: 1.65s; }
.home-grid > :nth-child(4) { animation-delay: 1.75s; }
.home-grid > :nth-child(5) { animation-delay: 1.85s; }
.home-grid > :nth-child(6) { animation-delay: 1.95s; }
.home-grid > :nth-child(n+7) { animation-delay: 2.05s; }

__KEYFRAMES__

@media (prefers-reduced-motion: reduce) {
    .home-26 *, .home-26 *::before, .home-26 *::after {
        animation-duration: 1ms !important;
        animation-delay: 0s !important;
    }
}
"""
_CSS = (_CSS.replace('__FONTS__', FONTS_IMPORT).replace('__TOKENS__', TOKENS)
        .replace('__KEYFRAMES__', KEYFRAMES).replace('__NOISE__', NOISE.replace('0 0 0 .5 0', '0 0 0 .35 0')))


def HomeHeader() -> Div:
    """Him & Her conference header for the home page, matching the coming soon page"""
    return Div(
        Style(_CSS),
        Div(Img(src='/assets/mas-logo-square.png', alt='MAS Logo'), Span('MAS Dallas'), cls='home-brand'),
        P('4th Annual CYP Conference', cls='home-eyebrow'),
        H1(*title_letters('HIM & HER', start_delay=.35, step=.07), cls='home-title', aria_label='Him & Her'),
        P('Building Success at Every Stage', cls='home-tagline'),
        Div(
            A(Icon('location-dot'), 'GEM Academy, Plano', href=VENUE_MAP_URL, target='_blank'),
            Span(Icon('calendar'), Span('Sat · Oct 24, 2026', cls='date')),
            cls='home-info',
        ),
        cls='home-header',
    )


def HimHerBanner() -> Div:
    """Compact Him & Her banner for inner pages (e.g. About)"""
    return Div(
        Style(_CSS),
        P('4th Annual CYP Conference', cls='home-eyebrow mt-0'),
        H1(*title_letters('HIM & HER', start_delay=.1, step=.05), cls='home-title', aria_label='Him & Her', style='font-size: clamp(64px, 20vw, 110px)'),
        P('Building Success at Every Stage', cls='home-tagline', style='animation-delay: .6s'),
        cls='home-header px-6 pt-2 pb-6',
    )

from fasthtml.common import Div, H1, P, Span, Img, Style

# Parchment grain, generated in-browser so no extra image asset is needed
_NOISE = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .45 0 0 0 0 .30 0 0 0 0 .12 0 0 0 .5 0'/></filter>"
    "<rect width='100%' height='100%' filter='url(%23n)'/></svg>"
)

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;600&display=swap');

.coming-soon {
    --cs-navy: #1c3765;
    --cs-navy-deep: #12264a;
    --cs-sand: #e8d6b1;
    --cs-tan: #c9a874;
    --cs-umber: #4f3519;
    position: fixed;
    inset: 0;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px 16px;
    color: var(--cs-navy);
    font-family: 'Oswald', sans-serif;
    text-align: center;
    background:
        radial-gradient(ellipse at 50% 42%, rgba(246, 234, 207, .95) 0%, rgba(232, 214, 177, .6) 35%, transparent 70%),
        radial-gradient(ellipse at 15% 85%, rgba(107, 77, 43, .45), transparent 55%),
        radial-gradient(ellipse at 90% 10%, rgba(107, 77, 43, .35), transparent 50%),
        linear-gradient(160deg, #d8bf92 0%, #c9a874 45%, #b28c58 100%);
    z-index: 50;
}

/* Paper grain */
.coming-soon::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("__NOISE__");
    opacity: .35;
    mix-blend-mode: multiply;
    pointer-events: none;
}

/* Vignette */
.coming-soon::after {
    content: '';
    position: absolute;
    inset: 0;
    box-shadow: inset 0 0 180px 40px rgba(70, 48, 22, .55);
    pointer-events: none;
}

/* Drifting smoky shapes echoing the flyer's double-exposure silhouettes */
.cs-smoke {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    mix-blend-mode: multiply;
    pointer-events: none;
}
.cs-smoke.one {
    width: 60vmax; height: 70vmax;
    left: -22vmax; top: -10vmax;
    background: radial-gradient(circle, rgba(120, 82, 40, .45), transparent 65%);
    animation: cs-drift-a 22s ease-in-out infinite alternate;
}
.cs-smoke.two {
    width: 55vmax; height: 65vmax;
    right: -20vmax; bottom: -15vmax;
    background: radial-gradient(circle, rgba(95, 66, 34, .45), transparent 65%);
    animation: cs-drift-b 26s ease-in-out infinite alternate;
}
.cs-smoke.three {
    width: 40vmax; height: 40vmax;
    left: 35%; top: 55%;
    background: radial-gradient(circle, rgba(255, 244, 220, .6), transparent 70%);
    mix-blend-mode: screen;
    animation: cs-drift-a 18s ease-in-out infinite alternate-reverse;
}

/* Light brush strokes */
.cs-strokes {
    position: absolute;
    inset: -20%;
    background: repeating-linear-gradient(115deg,
        transparent 0 38px,
        rgba(255, 246, 225, .05) 40px 44px,
        transparent 46px 90px);
    filter: blur(2px);
    animation: cs-sweep 30s linear infinite;
    pointer-events: none;
}

.cs-content {
    position: relative;
    z-index: 1;
    max-width: 920px;
    width: 100%;
}

.cs-brand {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    margin-bottom: clamp(20px, 5vh, 44px);
    opacity: 0;
    animation: cs-fade-down .9s ease-out .1s forwards;
}
.cs-brand img {
    width: 48px;
    height: 48px;
}
.cs-brand span {
    font-weight: 600;
    font-size: 14px;
    letter-spacing: .28em;
    text-transform: uppercase;
    color: var(--cs-navy-deep);
    text-align: left;
    line-height: 1.25;
}

.cs-eyebrow {
    font-weight: 600;
    font-size: clamp(14px, 2.4vw, 20px);
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--cs-navy-deep);
    opacity: 0;
    animation: cs-fade-down .9s ease-out .3s forwards;
}

.cs-title {
    font-family: 'Anton', 'Oswald', sans-serif;
    font-weight: 400;
    font-size: clamp(84px, 22vw, 230px);
    line-height: .9;
    margin: 8px 0 4px;
    color: var(--cs-navy);
    text-shadow: 0 2px 0 rgba(255, 245, 225, .25), 0 10px 30px rgba(60, 40, 15, .25);
    display: flex;
    justify-content: center;
    align-items: flex-end;
    white-space: nowrap;
}
.cs-title .ch {
    display: inline-block;
    opacity: 0;
    transform: translateY(60%);
    animation: cs-rise .8s cubic-bezier(.2, .8, .2, 1) forwards;
}
.cs-title .amp {
    font-size: .62em;
    margin: 0 -.04em .06em;
}

.cs-tagline {
    font-weight: 600;
    font-size: clamp(16px, 3.6vw, 34px);
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--cs-navy-deep);
    opacity: 0;
    animation: cs-fade-up .9s ease-out 1.5s forwards;
}

.cs-soon {
    position: relative;
    display: inline-block;
    margin-top: clamp(28px, 6vh, 56px);
    padding: 14px 4px 16px;
    font-family: 'Anton', 'Oswald', sans-serif;
    font-size: clamp(26px, 5vw, 44px);
    letter-spacing: .32em;
    margin-right: -.32em;
    text-transform: uppercase;
    background: linear-gradient(100deg, var(--cs-navy) 0%, var(--cs-navy) 40%, #5f7fb5 50%, var(--cs-navy) 60%, var(--cs-navy) 100%);
    background-size: 250% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    opacity: 0;
    animation: cs-fade-up .9s ease-out 1.9s forwards, cs-shimmer 4.5s ease-in-out 2.8s infinite;
}
.cs-soon::before,
.cs-soon::after {
    content: '';
    position: absolute;
    left: 50%;
    height: 2px;
    width: 0;
    background: var(--cs-navy);
    transform: translateX(-50%);
    animation: cs-line 1.1s ease-out 2.3s forwards;
}
.cs-soon::before { top: 0; }
.cs-soon::after { bottom: 0; }

.cs-details {
    margin-top: clamp(20px, 4vh, 36px);
    opacity: 0;
    animation: cs-fade-up .9s ease-out 2.5s forwards;
}
.cs-date {
    font-family: 'Anton', 'Oswald', sans-serif;
    font-size: clamp(22px, 4.2vw, 34px);
    letter-spacing: .04em;
    text-transform: uppercase;
    color: var(--cs-navy);
}
.cs-date .dot {
    display: inline-block;
    margin: 0 .5em;
    opacity: .5;
}
.cs-venue {
    margin-top: 4px;
    font-size: clamp(13px, 2.2vw, 16px);
    letter-spacing: .05em;
    color: var(--cs-umber);
}

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
@keyframes cs-line {
    to { width: 100%; }
}
@keyframes cs-shimmer {
    0% { background-position: 100% 0; }
    60%, 100% { background-position: 0% 0; }
}
@keyframes cs-drift-a {
    from { transform: translate(0, 0) scale(1); }
    to { transform: translate(6vmax, 4vmax) scale(1.08); }
}
@keyframes cs-drift-b {
    from { transform: translate(0, 0) scale(1.05); }
    to { transform: translate(-6vmax, -5vmax) scale(.95); }
}
@keyframes cs-sweep {
    from { transform: translateX(0); }
    to { transform: translateX(90px); }
}

@media (prefers-reduced-motion: reduce) {
    .coming-soon *,
    .coming-soon *::before,
    .coming-soon *::after {
        animation-duration: 1ms !important;
        animation-delay: 0s !important;
        animation-iteration-count: 1 !important;
    }
}
""".replace('__NOISE__', _NOISE)


def _title_letters(text: str, start_delay: float = .55, step: float = .09):
    """Split the headline into individually animated characters"""
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


def ComingSoon() -> Div:
    """Full-screen placeholder page styled after the Him & Her conference flyer"""
    return Div(
        Style(_CSS),
        Div(cls='cs-smoke one'),
        Div(cls='cs-smoke two'),
        Div(cls='cs-smoke three'),
        Div(cls='cs-strokes'),
        Div(
            Div(
                Img(src='/assets/mas-logo-square.png', alt='MAS Logo'),
                Span('MAS Dallas', cls='block'),
                cls='cs-brand',
            ),
            P('4th Annual CYP Conference', cls='cs-eyebrow'),
            H1(*_title_letters('HIM & HER'), cls='cs-title', aria_label='Him & Her'),
            P('Building Success at Every Stage', cls='cs-tagline'),
            Div('Coming Soon', cls='cs-soon'),
            Div(
                Div('Saturday', Span('•', cls='dot'), 'Oct 24', Span('•', cls='dot'), '11AM – 8PM', cls='cs-date'),
                P('GEM Academy & Facility · 6300 Independence Pkwy, Plano, TX 75023', cls='cs-venue'),
                cls='cs-details',
            ),
            cls='cs-content',
        ),
        cls='coming-soon',
    )

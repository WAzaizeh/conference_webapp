// Agenda tag filter (markup from TagFilter / agenda_timeline in components/timeline.py).
// No filter by default (every pill lit). Pills form two single-select groups that combine:
// one audience (data-track-tags, e.g. Masculinity) and one session type (Talk, Workshop, Prayer...).
// Picking another pill in the same group replaces it; tapping a selected pill clears it. A session must
// have every selected tag; sessions tagged "All" (for everyone) count as having the audience tags.
(function () {
    'use strict';

    const SHARED_TAG = 'All';
    const STORAGE_KEY = 'agenda-filter-and';

    function init() {
        const bar = document.getElementById('agenda-filter');
        if (!bar) return;
        const pills = [...bar.querySelectorAll('[data-tag]')];
        const clear = bar.querySelector('.tag-clear');
        const known = new Set(pills.map((p) => p.dataset.tag));
        const tracks = new Set(JSON.parse(bar.dataset.trackTags || '[]'));
        const sessions = [...document.querySelectorAll('li[data-tags]')].map((li) => ({ li, tags: JSON.parse(li.dataset.tags) }));

        let selected = new Set(load().filter((t) => known.has(t)));

        function render() {
            const filtering = selected.size > 0;
            pills.forEach((pill) => {
                const on = selected.has(pill.dataset.tag);
                pill.classList.toggle('active', !filtering || on);
                pill.setAttribute('aria-pressed', String(on));
            });
            clear.hidden = !filtering;
            sessions.forEach(({ li, tags }) => {
                const shared = tags.includes(SHARED_TAG);
                li.hidden = ![...selected].every((t) => tags.includes(t) || (shared && tracks.has(t)));
            });
            save([...selected]);
        }

        bar.addEventListener('click', (e) => {
            if (e.target.closest('.tag-clear')) {
                selected.clear();
            } else {
                const tag = e.target.closest('[data-tag]')?.dataset.tag;
                if (!tag) return;
                if (selected.has(tag)) {
                    selected.delete(tag);
                } else {
                    const group = (t) => tracks.has(t);  // true: audience, false: session type
                    [...selected].filter((t) => group(t) === group(tag)).forEach((t) => selected.delete(t));
                    selected.add(tag);
                }
            }
            render();
        });

        render();
    }

    // Remembering the filter is a convenience only; storage may be unavailable (private mode)
    function load() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; }
    }
    function save(tags) {
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(tags)); } catch { /* ignore */ }
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();

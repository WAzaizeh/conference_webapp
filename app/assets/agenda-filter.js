// Agenda tag filter (markup from TagFilter / agenda_timeline in components/timeline.py).
// No filter by default (no pill selected). Pills form two groups that combine:
// - audience (data-track-tags, e.g. Masculinity): single-select; picking another replaces it.
// - session type (Talk, Workshop, Prayer...): multi-select; a session matching any selected type is shown.
// Tapping a selected pill clears it. A session must match both groups (when used); sessions tagged
// "All" (for everyone) count as having the audience tags.
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
                pill.classList.toggle('active', on);
                pill.setAttribute('aria-pressed', String(on));
            });
            clear.hidden = !filtering;
            const audience = [...selected].filter((t) => tracks.has(t));
            const types = [...selected].filter((t) => !tracks.has(t));
            sessions.forEach(({ li, tags }) => {
                const shared = tags.includes(SHARED_TAG);
                const audienceOk = audience.every((t) => tags.includes(t) || shared);
                const typeOk = types.length === 0 || types.some((t) => tags.includes(t));
                li.hidden = !(audienceOk && typeOk);
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
                    // Audience is single-select: replace any other audience pill
                    if (tracks.has(tag)) [...selected].filter((t) => tracks.has(t)).forEach((t) => selected.delete(t));
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

// Agenda tag filter: pills start all selected. The first click narrows to that tag; further clicks
// add or remove tags; clearing every pill goes back to all. Sessions tagged "All" always stay visible.
// Markup comes from TagFilter / agenda_timeline in components/timeline.py.
(function () {
    'use strict';

    const SHARED_TAG = 'All';
    const STORAGE_KEY = 'agenda-filter';

    function init() {
        const bar = document.getElementById('agenda-filter');
        if (!bar) return;
        const pills = [...bar.querySelectorAll('[data-tag]')];
        const allTags = pills.map((p) => p.dataset.tag);
        const sessions = [...document.querySelectorAll('li[data-tags]')];

        let selected = new Set(load().filter((t) => allTags.includes(t)));
        if (!selected.size) selected = new Set(allTags);

        function render() {
            const showAll = selected.size === allTags.length;
            pills.forEach((pill) => {
                const on = selected.has(pill.dataset.tag);
                pill.classList.toggle('active', on);
                pill.setAttribute('aria-pressed', String(on));
            });
            sessions.forEach((li) => {
                const tags = JSON.parse(li.dataset.tags);
                li.hidden = !(showAll || tags.includes(SHARED_TAG) || tags.some((t) => selected.has(t)));
            });
            save(showAll ? [] : [...selected]);
        }

        bar.addEventListener('click', (e) => {
            const tag = e.target.closest('[data-tag]')?.dataset.tag;
            if (!tag) return;
            if (selected.size === allTags.length) selected = new Set([tag]);
            else if (selected.has(tag)) selected.delete(tag);
            else selected.add(tag);
            if (!selected.size) selected = new Set(allTags);
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

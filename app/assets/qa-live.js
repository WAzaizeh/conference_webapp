// Live Q&A: keeps a session's questions current over Server-Sent Events, updating only what changed.
// Runs only on pages rendered by QAPage (components/qa.py), which provides
// #qa-live[data-event-id][data-view][data-list-url] and #questions-list[data-sort].
(function () {
    'use strict';

    const MAX_FAILURES = 5;            // consecutive stream errors before falling back to polling
    const RECONNECT_MS = 3000;
    const FALLBACK_POLL_MS = 20000;
    const FLASH_MS = 4000;

    function init() {
        const root = document.getElementById('qa-live');
        if (!root) return;
        const { eventId, view, listUrl } = root.dataset;

        const list = () => document.getElementById('questions-list');
        const cards = () => [...list().querySelectorAll('[data-question-id]')];
        const cardById = (id) => document.getElementById('question-' + id);

        function toElement(html) {
            const template = document.createElement('template');
            template.innerHTML = html.trim();
            return template.content.firstElementChild;
        }

        // ---- Keeping the list consistent after any change ----

        function refreshList() {
            const sort = list() ? list().dataset.sort : 'popular';
            htmx.ajax('GET', `${listUrl}?sort=${sort}`, { target: '#questions-list', swap: 'outerHTML' });
        }

        function sortByPopularity() {
            const el = list();
            if (el.dataset.sort !== 'popular') return;
            cards()
                .sort((a, b) => (b.dataset.likes - a.dataset.likes) || b.dataset.created.localeCompare(a.dataset.created))
                .forEach((card) => el.appendChild(card));
        }

        function syncPageState() {
            const all = cards();
            const empty = list().querySelector('.qa-empty');
            if (empty) empty.style.display = all.length ? 'none' : '';

            const setStat = (key, value) => {
                const stat = document.getElementById('qa-stat-' + key);
                if (stat) stat.textContent = value;
            };
            setStat('total', all.length);
            setStat('visible', all.filter((c) => c.dataset.visible === 'true').length);
            setStat('answered', all.filter((c) => c.dataset.answered === 'true').length);

            document.querySelectorAll('[role=tab]').forEach((tab) =>
                tab.classList.toggle('tab-active', tab.id === list().dataset.sort + '-tab'));
        }

        function afterChange() {
            sortByPopularity();
            syncPageState();
        }

        // A broadcast card never carries this visitor's own like, so keep the one already shown
        function keepLikeState(from, to) {
            const old = from.querySelector('.qa-like');
            const fresh = to.querySelector('.qa-like');
            if (old && fresh) {
                fresh.classList.toggle('liked', old.classList.contains('liked'));
                fresh.setAttribute('aria-pressed', old.getAttribute('aria-pressed'));
            }
        }

        // ---- Stream messages (see utils/live/render.py) ----

        const handlers = {
            connected() {
                failures = 0;
                refreshList();  // catch up on anything missed before (re)connecting
            },
            card({ id, html }) {
                const card = toElement(html);
                const existing = cardById(id);
                if (existing) {
                    keepLikeState(existing, card);
                    existing.replaceWith(card);
                } else {
                    list().insertBefore(card, list().querySelector('[data-question-id]'));
                }
                htmx.process(card);
                afterChange();
            },
            remove({ id }) {
                const card = cardById(id);
                if (card) card.remove();
                afterChange();
            },
            likes({ id, likes }) {
                const card = cardById(id);
                if (!card) return;
                card.dataset.likes = likes;
                const count = document.getElementById('likes-' + id);
                if (count) count.textContent = likes;
                afterChange();
            },
            status({ active, html }) {
                const current = document.getElementById('qa-status');
                if (current) {
                    const updated = toElement(html);
                    current.replaceWith(updated);
                    htmx.process(updated);
                }
                const form = document.getElementById('question-form');
                if (form) form.querySelectorAll('input, textarea, button').forEach((el) => { el.disabled = !active; });
            },
        };

        // ---- Connection with automatic recovery ----

        let source = null;
        let failures = 0;

        function connect() {
            source = new EventSource(`/qa/event/${eventId}/stream?view=${view}`);
            Object.entries(handlers).forEach(([name, handle]) =>
                source.addEventListener(name, (e) => handle(JSON.parse(e.data))));
            source.onerror = () => {
                failures += 1;
                if (failures >= MAX_FAILURES) {
                    source.close();
                    setInterval(refreshList, FALLBACK_POLL_MS);  // e.g. a network that blocks streaming
                } else if (source.readyState === EventSource.CLOSED) {
                    setTimeout(connect, RECONNECT_MS);  // the browser only retries on its own while CONNECTING
                }
            };
        }

        // ---- Instant likes: show the change now, the server's card confirms it ----

        function flipLike(button) {
            const card = button.closest('[data-question-id]');
            const liked = !button.classList.contains('liked');
            button.classList.toggle('liked', liked);
            button.setAttribute('aria-pressed', String(liked));
            card.dataset.likes = Number(card.dataset.likes) + (liked ? 1 : -1);
            const count = document.getElementById('likes-' + card.dataset.questionId);
            if (count) count.textContent = card.dataset.likes;
        }

        document.addEventListener('htmx:beforeRequest', (e) => {
            if (e.detail.elt.classList.contains('qa-like')) flipLike(e.detail.elt);
        });
        ['htmx:responseError', 'htmx:sendError'].forEach((name) => document.addEventListener(name, (e) => {
            if (e.detail.elt.classList.contains('qa-like')) flipLike(e.detail.elt);  // undo
        }));

        // ---- After any htmx swap (tabs, likes, form) ----

        document.addEventListener('htmx:afterSettle', () => {
            if (list()) afterChange();
            document.querySelectorAll('.qa-flash:not([data-fading])').forEach((flash) => setTimeout(() => {
                flash.dataset.fading = 'true';
                flash.style.opacity = '0';
                setTimeout(() => flash.remove(), 500);
            }, FLASH_MS));
        });

        connect();
        window.addEventListener('pagehide', () => source && source.close());
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();

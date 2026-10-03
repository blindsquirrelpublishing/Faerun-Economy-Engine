"""Lore research desk, served with the application's embedded assets."""

LORE_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lore Desk | Faerun</title><link rel="stylesheet" href="lore.css"></head><body>
<header><a class="brand" href="index.html">Faerun <span>Economy Engine</span></a><nav aria-label="Main navigation"><a href="map.html">Map</a><a href="location.html">Locations</a><a href="index.html">Markets</a><a href="lore.html" aria-current="page">Lore</a></nav></header>
<main><div class="heading"><div><p class="eyebrow">Research &amp; correspondence / 1492 DR</p><h1>Lore Desk</h1></div><button id="new-thread" class="primary" type="button">+ New conversation</button></div>
<div class="desk-state"><span class="dot"></span><span>Asynchronous inbox</span><span class="muted">Agent runs in VS Code</span><button id="refresh" class="icon" title="Refresh desk" aria-label="Refresh desk" type="button">&#8635;</button></div>
<div id="notice" role="status" aria-live="polite"></div>
<div class="tabs" role="tablist" aria-label="Desk views"><button id="inbox-tab" role="tab" aria-selected="true" aria-controls="inbox">Conversations <span id="queue-count">0</span></button><button id="research-tab" role="tab" aria-selected="false" aria-controls="research" tabindex="-1">Reviewed research <span id="research-count">0</span></button></div>
<section id="inbox" role="tabpanel" aria-labelledby="inbox-tab"><div class="workspace"><aside aria-label="Conversations"><label for="search">Search conversations</label><input id="search" type="search" placeholder="Location, subject, message..."><label for="filter">Status</label><select id="filter"><option value="">All conversations</option><option value="queued">Awaiting Lore</option><option value="answered">Answered</option><option value="closed">Closed</option></select><div id="thread-list"></div></aside>
<section class="conversation" aria-label="Conversation"><div id="conversation-empty" class="empty"><h2>No conversation selected</h2><p class="muted">No messages yet.</p></div><div id="conversation-content" hidden><div class="conversation-heading"><div><p id="thread-meta" class="eyebrow"></p><h2 id="thread-title"></h2></div><button id="close-thread" type="button">Close conversation</button></div><div id="messages" aria-live="polite"></div><form id="reply-form"><label for="reply">Your reply</label><textarea id="reply" rows="4" maxlength="12000" required></textarea><div class="compose-actions"><span id="thread-state" class="muted"></span><button type="submit" class="primary">Send reply</button></div></form></div></section></div></section>
<section id="research" role="tabpanel" aria-labelledby="research-tab" hidden><div class="research-heading"><h2>Reviewed field notes</h2><span class="muted">Sourced lore / model assumptions kept separate</span></div><div id="research-list"></div></section>
</main><dialog id="new-dialog"><form id="new-form"><div class="dialog-heading"><h2>New conversation</h2><button class="icon" id="dismiss" type="button" aria-label="Close dialog" title="Close dialog">&#215;</button></div><label for="title">Subject</label><input id="title" maxlength="160" required placeholder="A location, trade good, or research lead"><label for="kind">Category</label><select id="kind"><option value="research">Research request</option><option value="question">Question</option><option value="map">Map proposal</option><option value="economy">Economy proposal</option></select><label for="body">Message</label><textarea id="body" rows="6" maxlength="12000" required></textarea><p id="dialog-error" role="alert"></p><div class="compose-actions"><span class="muted">Queued for Lore</span><button type="submit" class="primary">Send request</button></div></form></dialog>
<script src="lore.js"></script></body></html>"""

LORE_CSS = """
:root{--ink:#25352f;--green:#295e4b;--paper:#fafbf9;--line:#d8dfda;--muted:#626c66;--red:#873b49}*{box-sizing:border-box;letter-spacing:0}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 'Segoe UI',sans-serif}header{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:18px 4%;border-bottom:1px solid var(--line);background:white}a{color:var(--green);text-underline-offset:4px}.brand{font:700 23px Georgia,serif;text-decoration:none;color:var(--ink)}.brand span{font:12px 'Segoe UI',sans-serif;display:block;text-transform:uppercase;letter-spacing:0}nav{display:flex;flex-wrap:wrap;gap:22px}nav a{text-decoration:none;font-size:14px}nav [aria-current]{border-bottom:2px solid var(--green)}main{max-width:1440px;margin:auto;padding:32px 4% 60px}.heading,.desk-state,.conversation-heading,.dialog-heading,.compose-actions,.research-heading{display:flex;align-items:center;justify-content:space-between;gap:16px}.eyebrow{text-transform:uppercase;font-size:11px;font-weight:700;color:var(--muted);margin:0 0 5px}h1{font:40px/1.15 Georgia,serif;margin:0 0 12px}h2{font:25px/1.25 Georgia,serif;margin:0;overflow-wrap:anywhere}h3{font:23px Georgia,serif;margin:0 0 10px}.muted{color:var(--muted);font-size:13px}button,input,select,textarea{font:inherit}button{border:1px solid var(--line);background:white;color:var(--ink);padding:8px 13px;border-radius:4px;cursor:pointer;line-height:1.4}button:hover{border-color:var(--green);background:#edf3ef}button:disabled{opacity:.5;cursor:default}.primary{background:var(--green);border-color:var(--green);color:white}.primary:hover{background:#214b3c;color:white}button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:2px solid var(--red);outline-offset:3px}.icon{width:38px;height:38px;flex-shrink:0;padding:0;font-size:23px}.desk-state{justify-content:flex-start;font-size:13px;margin:17px 0 10px;border-top:1px solid var(--line);padding-top:14px}.desk-state .icon{margin-left:auto}.dot{width:8px;height:8px;background:#ae8240;border-radius:50%;flex-shrink:0}#notice{font-size:13px;min-height:27px;color:var(--green)}#notice.error,#dialog-error{color:var(--red)}.tabs{display:flex;gap:22px;border-bottom:1px solid var(--line)}.tabs button{border:0;border-radius:0;background:transparent;padding:12px 0}.tabs [aria-selected=true]{border-bottom:3px solid var(--green);font-weight:600}.tabs span{font-size:11px;padding:2px 6px;background:#e8ede9;border-radius:3px;margin-left:6px}.workspace{display:grid;grid-template-columns:290px minmax(0,1fr);min-height:550px}aside{padding:22px 20px 22px 0;border-right:1px solid var(--line)}label{display:block;font-size:12px;font-weight:600;margin:10px 0 5px}input,select,textarea{width:100%;border:1px solid #b9c5bd;border-radius:4px;background:white;padding:9px;color:var(--ink);min-width:0}textarea{resize:vertical}#thread-list{margin-top:22px}.thread{display:block;text-align:left;width:100%;border:0;border-bottom:1px solid var(--line);border-radius:0;background:transparent;padding:15px 10px;overflow-wrap:anywhere}.thread[aria-current=true]{background:#eaf1eb;border-left:3px solid var(--green)}.thread strong{display:block;font-size:14px}.thread small{font-size:11px;color:var(--muted)}.conversation{min-width:0;padding:26px 0 0 30px}.conversation-heading{align-items:flex-start;border-bottom:1px solid var(--line);padding-bottom:18px}.conversation-heading button{font-size:12px;flex-shrink:0}.empty{padding:70px 15px;text-align:center}.message{padding:22px 0;border-bottom:1px solid var(--line)}.message-header{display:flex;gap:12px;align-items:baseline;font-size:12px}.message-header strong{color:var(--green)}.message[data-author=You] .message-header strong{color:var(--red)}.message-body{white-space:pre-wrap;overflow-wrap:anywhere;margin:9px 0;font-size:15px}.sources{display:flex;flex-wrap:wrap;gap:12px;font-size:13px;overflow-wrap:anywhere}#reply-form{margin-top:22px}.compose-actions{margin-top:13px;flex-wrap:wrap}.research-heading{margin:25px 0}.research-entry{display:grid;grid-template-columns:190px minmax(0,1fr);gap:32px;border-bottom:1px solid var(--line);padding:28px 0}.research-entry p{margin:0 0 16px;overflow-wrap:anywhere}.research-entry .era{border-left:3px solid #b48747;padding-left:15px;font-size:13px;color:var(--muted)}.research-entry a{overflow-wrap:anywhere}.research-entry summary{cursor:pointer;color:var(--green);font-size:14px;margin-bottom:16px}dialog{border:1px solid var(--line);border-radius:6px;width:min(580px,calc(100% - 32px));max-height:90vh;padding:26px;color:var(--ink);background:var(--paper)}dialog::backdrop{background:#152e2580}dialog h2{font-size:25px}.dialog-heading{margin-bottom:20px}[hidden]{display:none!important}@media(max-width:760px){header{align-items:flex-start;padding:15px 5%;flex-direction:column;gap:12px}nav{gap:20px}main{padding:23px 5%}.heading{align-items:flex-start;flex-wrap:wrap}h1{font-size:34px}.heading button{font-size:13px}.desk-state{gap:9px;flex-wrap:wrap}.workspace{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid var(--line);padding:14px 0}#thread-list{max-height:210px;overflow:auto}.conversation{padding:22px 0}.conversation-heading{flex-wrap:wrap}.tabs{gap:18px}.tabs button{font-size:13px}.research-entry{grid-template-columns:1fr;gap:12px}.research-heading{align-items:flex-start;flex-direction:column}.empty{padding:38px 0}}
"""

LORE_JS = r"""
'use strict';
const el = id => document.getElementById(id);
const state = {threads: [], research: [], selected: null, busy: false, loading: false};
const labels = {queued: 'Awaiting Lore', answered: 'Answered', closed: 'Closed'};
function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}
function notice(text, error = false) { el('notice').textContent = text; el('notice').className = error ? 'error' : ''; }
async function api(body) {
  const response = await fetch('/api/lore-desk', body === undefined ? {cache: 'no-store'} : {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Lore desk is unavailable.');
  return data;
}
function sourceLinks(sources) {
  const links = node('div', undefined, 'sources');
  for (const source of sources || []) {
    try {
      const url = new URL(source.url);
      if (!['https:', 'http:'].includes(url.protocol)) continue;
      const link = node('a', source.title || source.url);
      link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer';
      links.append(link);
    } catch (_) {}
  }
  return links;
}
function renderThreads() {
  const query = el('search').value.toLowerCase();
  const threads = state.threads.filter(thread => (!el('filter').value || thread.status === el('filter').value) &&
    (thread.title + ' ' + thread.messages.map(message => message.body).join(' ')).toLowerCase().includes(query));
  el('thread-list').replaceChildren();
  for (const thread of threads) {
    const button = node('button', undefined, 'thread'); button.type = 'button';
    button.setAttribute('aria-current', String(thread.id === state.selected));
    button.append(node('strong', thread.title), node('small', labels[thread.status] + ' / ' + thread.kind));
    button.onclick = () => {
      if (state.selected !== thread.id && el('reply').value.trim() && !confirm('Discard the unsent reply?')) return;
      if (state.selected !== thread.id) el('reply').value = '';
      state.selected = thread.id; renderThreads(); renderConversation();
    };
    el('thread-list').append(button);
  }
  if (!threads.length) el('thread-list').append(node('p', 'No conversations found.', 'muted'));
  el('queue-count').textContent = state.threads.filter(thread => thread.status === 'queued').length;
}
function renderConversation() {
  const thread = state.threads.find(thread => thread.id === state.selected);
  el('conversation-empty').hidden = !!thread; el('conversation-content').hidden = !thread;
  if (!thread) return;
  el('thread-title').textContent = thread.title;
  el('thread-meta').textContent = thread.kind + ' / ' + labels[thread.status];
  el('close-thread').textContent = thread.status === 'closed' ? 'Reopen conversation' : 'Close conversation';
  el('messages').replaceChildren();
  for (const message of thread.messages) {
    const article = node('article', undefined, 'message'); article.dataset.author = message.author;
    const heading = node('div', undefined, 'message-header');
    heading.append(node('strong', message.author), node('span', new Date(message.created).toLocaleString(), 'muted'));
    article.append(heading, node('p', message.body, 'message-body'), sourceLinks(message.sources));
    el('messages').append(article);
  }
  el('reply-form').hidden = thread.status === 'closed';
  el('thread-state').textContent = labels[thread.status];
}
function renderResearch() {
  el('research-count').textContent = state.research.length;
  el('research-list').replaceChildren();
  for (const entry of state.research) {
    const article = node('article', undefined, 'research-entry');
    const title = node('div');
    const name = entry.id === 'griffon_s_nest' ? "Griffon's Nest" : entry.id.replaceAll('_', ' ').replace(/\b\w/g, char => char.toUpperCase());
    title.append(node('h3', name), node('p', entry.status, 'eyebrow'));
    const link = node('a', 'Location record'); link.href = 'location.html?settlement=' + encodeURIComponent(entry.id); title.append(link);
    const content = node('div');
    content.append(node('p', (entry.paragraphs || [])[0] || 'No reviewed summary.'));
    const details = node('details'); details.append(node('summary', 'Full research notes'));
    for (const paragraph of (entry.paragraphs || []).slice(1)) details.append(node('p', paragraph));
    details.append(node('p', entry.era_note, 'era')); content.append(details, sourceLinks(entry.sources));
    for (const source of entry.sources || []) content.append(node('p', [source.kind, source.accessed && 'Accessed ' + source.accessed].filter(Boolean).join(' / '), 'muted'));
    article.append(title, content); el('research-list').append(article);
  }
}
async function refresh() {
  if (state.loading) return;
  state.loading = true;
  try {
    const data = await api();
    const researchChanged = JSON.stringify(state.research) !== JSON.stringify(data.research);
    const threadsChanged = JSON.stringify(state.threads) !== JSON.stringify(data.threads);
    state.threads = data.threads; state.research = data.research;
    if (threadsChanged) { renderThreads(); renderConversation(); }
    else renderThreads();
    if (researchChanged) renderResearch();
    notice('Desk up to date.');
  } catch (error) { notice(error.message, true); }
  finally { state.loading = false; }
}
async function mutate(body) {
  if (state.busy) return null;
  state.busy = true;
  document.querySelectorAll('button[type=submit]').forEach(button => button.disabled = true);
  el('close-thread').disabled = true;
  try { return await api(body); }
  finally {
    state.busy = false;
    document.querySelectorAll('button[type=submit]').forEach(button => button.disabled = false);
    el('close-thread').disabled = false;
  }
}
el('new-thread').onclick = () => { el('dialog-error').textContent = ''; el('new-dialog').showModal(); };
el('dismiss').onclick = () => el('new-dialog').close();
el('new-form').onsubmit = async event => {
  event.preventDefault();
  try {
    const result = await mutate({title: el('title').value, kind: el('kind').value, body: el('body').value});
    if (!result) return;
    state.selected = result.id; el('reply').value = ''; el('new-form').reset(); el('new-dialog').close();
    el('filter').value = ''; el('search').value = ''; showView('inbox'); await refresh();
  } catch (error) { el('dialog-error').textContent = error.message; }
};
el('reply-form').onsubmit = async event => {
  event.preventDefault();
  try {
    const result = await mutate({action: 'reply', id: state.selected, body: el('reply').value});
    if (!result) return;
    el('reply').value = ''; await refresh();
  } catch (error) { notice(error.message, true); }
};
el('close-thread').onclick = async () => {
  const thread = state.threads.find(thread => thread.id === state.selected);
  if (!thread) return;
  try { await mutate({action: 'status', id: thread.id, status: thread.status === 'closed' ? 'queued' : 'closed'}); await refresh(); }
  catch (error) { notice(error.message, true); }
};
function showView(view) {
  for (const name of ['inbox', 'research']) {
    el(name).hidden = name !== view; el(name + '-tab').setAttribute('aria-selected', String(name === view));
    el(name + '-tab').tabIndex = name === view ? 0 : -1;
  }
}
for (const name of ['inbox', 'research']) {
  el(name + '-tab').onclick = () => showView(name);
  el(name + '-tab').onkeydown = event => {
    if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      const next = event.key === 'Home' ? 'inbox' : event.key === 'End' ? 'research' : name === 'inbox' ? 'research' : 'inbox';
      showView(next); el(next + '-tab').focus();
    }
  };
}
el('search').oninput = renderThreads; el('filter').onchange = renderThreads;
el('refresh').onclick = refresh;
window.addEventListener('beforeunload', event => { if (el('reply').value.trim() || el('body').value.trim() || el('title').value.trim()) { event.preventDefault(); event.returnValue = ''; } });
refresh();
setInterval(() => { if (!document.hidden && !state.busy) refresh(); }, 15000);
"""

LORE_ASSETS = {
    "lore.html": (LORE_HTML, "text/html; charset=utf-8"),
    "lore.css": (LORE_CSS, "text/css; charset=utf-8"),
    "lore.js": (LORE_JS, "application/javascript; charset=utf-8"),
}
"""Presentation for the read-only listener; write enforcement lives in web.py."""

READ_ONLY_HEAD = """
<style id="read-only-style">
#read-only-notice {
  position: fixed; bottom: 12px; right: 12px; z-index: 10000;
  padding: 8px 14px; border: 1px solid #295e4b; border-radius: 6px;
  background: #fafbf9; color: #25352f; font: 14px/1.4 system-ui, sans-serif;
  pointer-events: none;
}
label:has(#month-select), label:has(#year-input), label:has(#seed-input),
label:has(#seasonal-toggle), #apply-world, #rebuild,
.event-editor, .event-actions, .leg-editor,
[aria-label="Map location editor"], #calib-row, #calib-tools,
#calib-help-row, #atlas-row, label:has(#opt-terrain-edit),
label:has(#terrain-edit-type), #terrain-edit-help,
#quote-form, #reserve-form, #payment-form, #action-inputs,
#request-form, #bid-form, #request-actions, .accept-bid, .withdraw-bid,
#new-thread, #close-thread, #reply-form, #new-dialog,
a[href="lore.html"], a[href="/lore.html"] {
  display: none !important;
}
.events-page .events-layout { grid-template-columns: minmax(0, 1fr); }
</style>
"""

READ_ONLY_NOTICE = (
    '<div id="read-only-notice" role="status">'
    'Read-only view - changes disabled</div>'
)

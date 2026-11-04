// Paste into Extensions > Apps Script in the league's Google Sheet.
// Deploy as a web app: Execute as Me, Who has access: Anyone.
// To approve a trade, change its status in the "Site trades" tab to approved or rejected.
const TAB = 'Site trades';
function tab_() {
  const ss = SpreadsheetApp.getActive();
  let s = ss.getSheetByName(TAB);
  if (!s) { s = ss.insertSheet(TAB); s.appendRow(['status', 'submitted', 'trade', 'ts', 'tx', 'sides']); }
  return s;
}
function doGet() {
  const rows = tab_().getDataRange().getValues().slice(1);
  const trades = rows.map((r, i) => ({ id: 'r' + (i + 2), status: String(r[0]).trim().toLowerCase(), ts: Number(r[3]), tx: r[4], sides: JSON.parse(r[5]) }))
    .filter(t => t.status === 'approved' || t.status === 'pending' || t.status === 'rejected');
  return ContentService.createTextOutput(JSON.stringify({ trades })).setMimeType(ContentService.MimeType.JSON);
}
function doPost(e) {
  const b = JSON.parse(e.postData.contents);
  tab_().appendRow(['pending', new Date(), String(b.summary).slice(0, 500), Number(b.ts), String(b.tx || ''), JSON.stringify(b.sides).slice(0, 5000)]);
  return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
}

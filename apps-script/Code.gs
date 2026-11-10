// Paste into Extensions > Apps Script in a Google Sheet, then deploy as a web app
// (Execute as: Me, Who has access: Anyone). Change PASSCODE before deploying.
const PASSCODE = 'CHANGE-ME';
const TAB = 'Site trades';
function tab_() {
  const ss = SpreadsheetApp.getActive();
  let s = ss.getSheetByName(TAB);
  if (!s) { s = ss.insertSheet(TAB); s.appendRow(['status', 'submitted', 'trade', 'ts', 'tx', 'sides']); }
  return s;
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function doGet() {
  const rows = tab_().getDataRange().getValues().slice(1);
  const trades = rows.map((r, i) => ({ id: 'r' + (i + 2), status: String(r[0]).trim().toLowerCase(), ts: Number(r[3]), tx: r[4], sides: r[5] ? JSON.parse(r[5]) : [] }))
    .filter(t => ['approved', 'pending', 'rejected'].includes(t.status));
  return out_({ trades });
}
function doPost(e) {
  const b = JSON.parse(e.postData.contents);
  const s = tab_();
  if (b.action === 'submit') {
    s.appendRow(['pending', new Date(), String(b.summary).slice(0, 500), Number(b.ts), String(b.tx || ''), JSON.stringify(b.sides).slice(0, 5000)]);
    return out_({ ok: true });
  }
  if (b.pass !== PASSCODE) return out_({ ok: false, error: 'passcode' });
  const row = Number(String(b.id).slice(1));
  if (!(row >= 2 && row <= s.getLastRow())) return out_({ ok: false, error: 'row' });
  if (b.action === 'approve') s.getRange(row, 1).setValue('approved');
  else if (b.action === 'reject') s.getRange(row, 1).setValue('rejected');
  else if (b.action === 'delete') s.getRange(row, 1).setValue('deleted');
  else return out_({ ok: false, error: 'action' });
  return out_({ ok: true });
}

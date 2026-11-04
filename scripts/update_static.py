"""Refreshes data/static.json from Sleeper. Run daily by GitHub Actions."""
import json,urllib.request
LEAGUE='1322003838051323904'
def get(u):
    req=urllib.request.Request('https://api.sleeper.app/v1/'+u,headers={'User-Agent':'edgers-league-hub'})
    return json.load(urllib.request.urlopen(req,timeout=120))
P=get('players/nfl')
sheet=json.load(open('data/sheet.json'))
cur=get(f'league/{LEAGUE}/rosters');o2r={r['owner_id']:r['roster_id'] for r in cur}
def nm(i):
    p=P.get(i) or {}
    return p.get('full_name') or ' '.join(x for x in [p.get('first_name'),p.get('last_name')] if x) or i
L=LEAGUE;trades=[];drafts=[];champs=[];first=True;draftEnd=0
while L and L!='0':
    lg=get(f'league/{L}')
    if not lg:break
    rr=get(f'league/{L}/rosters');own={r['roster_id']:o2r.get(r['owner_id']) for r in rr}
    for w in range(1,19):
        for t in get(f'league/{L}/transactions/{w}') or []:
            if t['type']!='trade' or t['status']!='complete':continue
            sides=[]
            for r in t['roster_ids']:
                a=[nm(k) for k,v in (t.get('drops') or {}).items() if v==r]+[f"{p['season']} Rd {p['round']}" for p in t.get('draft_picks') or [] if p['previous_owner_id']==r]+[f"${b['amount']} FAAB" for b in t.get('waiver_budget') or [] if b['sender']==r]
                sides.append([own.get(r),a])
            trades.append(dict(season=lg['season'],ts=t['status_updated'],sides=sides))
    for d in get(f'league/{L}/drafts') or []:
        dd=get(f"draft/{d['draft_id']}")
        if dd['status']!='complete':continue
        s2r=dd.get('slot_to_roster_id') or {};rows=[]
        for p in get(f"draft/{d['draft_id']}/picks") or []:
            m=p.get('metadata') or {};pl=P.get(p['player_id']) or {}
            name=pl.get('full_name') or (m.get('first_name','')+' '+m.get('last_name','')).strip() or p['player_id']
            rows.append([p['round'],p['draft_slot'],p['pick_no'],name,pl.get('position') or m.get('position') or '?',own.get(p['roster_id']),own.get(s2r.get(str(p['draft_slot'])))])
        drafts.append(dict(id=d['draft_id'],season=dd['season'],type=dd['type'],teams=dd['settings'].get('teams'),start=dd.get('start_time'),slots={k:own.get(v) for k,v in s2r.items()},picks=rows))
        draftEnd=max(draftEnd,dd.get('last_picked') or 0)
    if not first:
        br=get(f'league/{L}/winners_bracket') or [];uu={u['user_id']:u for u in get(f'league/{L}/users')};owner={x['roster_id']:x['owner_id'] for x in rr}
        fin=[b for b in br if b.get('p')==1]
        n=lambda rid:(lambda u:((u.get('metadata') or {}).get('team_name') or u.get('display_name'),u.get('display_name')))(uu.get(owner.get(rid),{}))
        if fin: champs.append(dict(season=lg['season'],champ=n(fin[0]['w']),runner=n(fin[0]['l'])))
    first=False;L=lg.get('previous_league_id')
trades.sort(key=lambda x:-x['ts']);drafts.sort(key=lambda x:(-int(x['season']),-(x['start'] or 0)))
keep=('QB','RB','WR','TE','K','DEF')
players={i:[nm(i),p.get('position') or '?',p.get('team') or 'FA',p.get('injury_status') or ''] for i,p in P.items() if p.get('position') in keep and (p.get('team') or p.get('active'))}
ids=set()
for r in cur:
    ids.update(r['players'] or [])
for i in ids:
    if i not in players and i in P: players[i]=[nm(i),P[i].get('position') or '?',P[i].get('team') or 'FA',P[i].get('injury_status') or '']
out=dict(players=players,drafts=drafts,champs=champs,draftEnd=draftEnd,dues=sheet['dues'],lastCycle=sheet['lastCycle'],hist=dict(sleeper=trades,sheet=sheet['sheetLog']))
json.dump(out,open('data/static.json','w'),separators=(',',':'))
print(len(players),len(trades),len(drafts),champs[:1])

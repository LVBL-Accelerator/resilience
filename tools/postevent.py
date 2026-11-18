#!/usr/bin/env python3
"""Keep the record of what a cyclone did after it crossed the coast.

    python3 tools/postevent.py --add "deaths" --value "12" --source "..." --note "..."
    python3 tools/postevent.py --show
    python3 tools/postevent.py --landfall "2026-11-20T11:30+05:30" --where "between Nellore and Tuni"
    python3 tools/postevent.py --cleared "2026-11-20T20:00+05:30" --where "the rear bands over Rayalaseema"

The event page is a live document while the storm is at sea. Afterwards the
question changes: how many died, how many were in shelters, how much crop was
lost, what the rainfall was, when the power came back. Those numbers arrive over
days and from many places, so they are appended here with their source and the
time they were found, never overwritten, and the page can be rebuilt from them.
"""
import argparse, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVENT = json.load(open(os.path.join(ROOT, 'data', 'event.json')))['event']
RECORD = os.path.join(ROOT, 'data', '%s-postevent.json' % EVENT)

def now():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=5, minutes=30))).isoformat(timespec='seconds')

def load():
    if os.path.exists(RECORD):
        return json.load(open(RECORD))
    return {'event': EVENT, 'landfall': None, 'cleared': None, 'entries': []}

def save(d):
    json.dump(d, open(RECORD, 'w'), indent=2)
    open(RECORD, 'a').write('\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--add')
    ap.add_argument('--value')
    ap.add_argument('--source')
    ap.add_argument('--note')
    ap.add_argument('--landfall')
    ap.add_argument('--cleared')
    ap.add_argument('--where')
    ap.add_argument('--show', action='store_true')
    a = ap.parse_args()
    d = load()
    if a.show:
        print(json.dumps(d, indent=2)); return
    if a.landfall:
        d['landfall'] = {'at': a.landfall, 'where': a.where, 'logged': now()}
        save(d); print('landfall recorded: %s %s' % (a.landfall, a.where or '')); return
    if a.cleared:
        d['cleared'] = {'at': a.cleared, 'where': a.where, 'logged': now()}
        save(d); print('rear of the system cleared: %s %s' % (a.cleared, a.where or '')); return
    if not a.add:
        sys.exit('nothing to do: pass --add FIELD or --landfall TIME')
    d['entries'].append({'field': a.add, 'value': a.value, 'source': a.source,
                         'note': a.note, 'found': now(),
                         'phase': 'provisional' if not d.get('cleared') else 'settled'})
    save(d)
    print('%s: %s (%d entries)' % (a.add, a.value, len(d['entries'])))

if __name__ == '__main__':
    main()

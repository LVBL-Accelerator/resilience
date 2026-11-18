#!/usr/bin/env python3
"""Write the observation record out as a track file.

    python3 export_track.py                 # writes data/<event>-track.csv
    python3 export_track.py --check         # reports the count and the gaps

The record in data/observations.json is the source of truth. This script never
edits it; it only reads. Run it after every poller update, and once more when
the event closes, so the track survives the page.
"""
import csv, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # resilience/
RECORD = os.path.join(ROOT, 'data', 'observations.json')

def load():
    with open(RECORD) as f:
        return json.load(f)

def main():
    d = load()
    obs = sorted(d['observations'], key=lambda o: o['issue'])
    event = d.get('event', 'event')
    out = os.path.join(ROOT, 'data', '%s-track.csv' % event)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['issue_ist', 'lat', 'lon', 'intensity', 'movement', 'where', 'fetched'])
        for o in obs:
            w.writerow([o['issue'], o['lat'], o['lon'], o.get('intensity', ''),
                        o.get('movement', ''), o.get('where', ''), o.get('fetched', '')])
    # a gap is more than four hours between consecutive fixes
    gaps = []
    for a, b in zip(obs, obs[1:]):
        ta = datetime.datetime.fromisoformat(a['issue'])
        tb = datetime.datetime.fromisoformat(b['issue'])
        if (tb - ta).total_seconds() > 4 * 3600:
            gaps.append('%s to %s' % (a['issue'][5:16], b['issue'][5:16]))
    print('%d fixes in %s' % (len(obs), os.path.relpath(out, ROOT)))
    print('first %s, last %s' % (obs[0]['issue'][5:16], obs[-1]['issue'][5:16]))
    if gaps:
        print('gaps longer than four hours: %s' % '; '.join(gaps))
    else:
        print('no gap longer than four hours')
    if '--check' in sys.argv:
        return
    print('written')

if __name__ == '__main__':
    main()

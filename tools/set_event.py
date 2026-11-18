#!/usr/bin/env python3
"""One place for what an event is called, and everything else follows it.

    python3 tools/set_event.py --descriptor "Severe Cyclonic Storm"
    python3 tools/set_event.py --status ended

The name and the descriptor change several times in a storm's life, and the same
fact used to be written in the event page and in the index page separately, which
is how they came to disagree. data/event.json now holds it, and this script
rewrites both pages from it so they cannot drift. The pages also read the JSON at
runtime, so a fresh copy corrects an older page.
"""
import argparse, json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data', 'event.json')

def load():
    return json.load(open(DATA))

def save(d):
    d['updated'] = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=5, minutes=30))).isoformat(timespec='seconds')
    json.dump(d, open(DATA, 'w'), indent=2)
    open(DATA, 'a').write('\n')

def title_of(d):
    """The words in front of the name, as the suite writes them in a heading."""
    desc = d['descriptor']
    if desc.lower().startswith('cyclonic storm'):
        return 'Cyclone ' + d['name']
    return desc + ' ' + d['name']

def render(d):
    t = title_of(d)
    # the event page
    p = os.path.join(ROOT, 'events', d['event'] + '.html')
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<h1 class="header__title">.*?</h1>',
               '<h1 class="header__title">%s <span class="header__title-note">%s</span></h1>' % (t, d['note']), s, count=1, flags=re.S)
    s = re.sub(r'<title>[^<]*</title>', '<title>%s &mdash; Resilience</title>' % t, s, count=1)
    open(p, 'w', encoding='utf-8').write(s)
    # the live row on the index page
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    row = re.search(r'(<a class="evline[^"]*" href="%s">.*?</a>)' % re.escape(d['page']), s, re.S)
    if row:
        new = ('<a class="evline evline--live" href="%s"><div class="evline__top">'
               '<span class="evline__date">%s</span><span class="evline__live">live</span></div>'
               '<div class="evline__name">%s</div><div class="evline__where">%s</div></a>'
               % (d['page'], d['since_label'], t, d['states']))
        s = s[:row.start()] + new + s[row.end():]
        open(p, 'w', encoding='utf-8').write(s)
    else:
        print('warning: no live row found on the index page for %s' % d['page'])
    return t

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--descriptor')
    ap.add_argument('--name')
    ap.add_argument('--status', choices=['live', 'ended'])
    ap.add_argument('--since-label')
    ap.add_argument('--show', action='store_true')
    a = ap.parse_args()
    d = load()
    if a.descriptor: d['descriptor'] = a.descriptor
    if a.name: d['name'] = a.name
    if a.status: d['status'] = a.status
    if a.since_label: d['since_label'] = a.since_label
    if a.show:
        print(json.dumps(d, indent=2)); return
    save(d)
    print('title now: %s' % render(d))

if __name__ == '__main__':
    main()

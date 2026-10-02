# -*- coding: utf-8 -*-
"""Cut every wall or cabinet a Richelieu Gola channel's recess really cuts (and uncut those it no longer touches).

Backup for the automatic updater: use it on models edited without the extension loaded.
Cuts Revit refuses (for example a circular chain of references) are listed with Revit's reason;
the other cuts still go through. A channel placed on an in-place element (which Revit cannot cut
from a channel sitting on it) is first replaced by an identical unhosted copy; those are listed.
"""
__title__ = 'Cut Gola\nRecesses'
import gola_autocut

doc = __revit__.ActiveUIDocument.Document
rows = gola_autocut.apply(doc, gola_autocut.gola_instances(doc))
added = sum(len(r[1]) for r in rows)
removed = sum(len(r[2]) for r in rows)
blocked = sorted(set(b for r in rows for b in r[3]))
refused = [(r[0], d, w) for r in rows for d, w in r[4]]
replaced = [r[5] for r in rows if len(r) > 5 and r[5] and ' replaced by ' in r[5]]
print('Gola channels checked: %d. Cuts added: %d. Cuts removed: %d.' % (len(rows), added, removed))
for m in replaced:
    print(m)
for gid, d, w in refused:
    print('Gola %d could not cut %s: %s' % (gid, d, w))
if blocked:
    print('Touching but not cuttable by voids:')
    for b in blocked: print('  ' + b)
print('Details: ' + gola_autocut.LOG)

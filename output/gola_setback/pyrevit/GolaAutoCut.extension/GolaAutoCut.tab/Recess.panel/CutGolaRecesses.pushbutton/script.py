# -*- coding: utf-8 -*-
"""Cut every wall or cabinet touched by a Richelieu Gola channel in the active model (and uncut those no longer touched).

Backup for the automatic updater: use it on models edited without the extension loaded.
"""
__title__ = 'Cut Gola\nRecesses'
from Autodesk.Revit import DB
import gola_autocut

doc = __revit__.ActiveUIDocument.Document
insts = gola_autocut.gola_instances(doc)
tx = DB.Transaction(doc, 'Cut Gola Recesses'); tx.Start()
added = removed = 0
blocked = set()
for inst in insts:
    a, r, b = gola_autocut.sync(doc, inst)
    added += len(a); removed += len(r); blocked.update(b)
tx.Commit()
print('Gola channels checked: %d. Cuts added: %d. Cuts removed: %d.' % (len(insts), added, removed))
if blocked:
    print('Not cut (turn on "Cut with Voids When Loaded" in these families, reload them, then run this again):')
    for b in sorted(blocked): print('  ' + b)

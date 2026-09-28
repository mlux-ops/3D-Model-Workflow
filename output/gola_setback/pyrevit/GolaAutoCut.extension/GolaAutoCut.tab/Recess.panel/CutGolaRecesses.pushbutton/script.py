# -*- coding: utf-8 -*-
"""Cut every wall touched by a Richelieu Gola channel in the active model (and uncut walls no longer touched).

Backup for the automatic updater: use it on models edited without the extension loaded.
"""
__title__ = 'Cut Gola\nRecesses'
from Autodesk.Revit import DB
import gola_autocut

doc = __revit__.ActiveUIDocument.Document
insts = gola_autocut.gola_instances(doc)
tx = DB.Transaction(doc, 'Cut Gola Recesses'); tx.Start()
added = removed = 0
for inst in insts:
    a, r = gola_autocut.sync(doc, inst)
    added += len(a); removed += len(r)
tx.Commit()
print('Gola channels checked: %d. Wall cuts added: %d. Cuts removed: %d.' % (len(insts), added, removed))

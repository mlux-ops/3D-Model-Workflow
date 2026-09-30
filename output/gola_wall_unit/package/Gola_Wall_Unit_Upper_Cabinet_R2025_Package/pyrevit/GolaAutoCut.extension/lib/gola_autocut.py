# -*- coding: utf-8 -*-
"""Automatic recess cuts for Richelieu Gola two-click (line-based) families.

Revit only auto-cuts hosts with voids for face- and wall-based templates. The Gola families
are line based (two-click placement), so this module applies the same cut Revit's
Cut Geometry makes (InstanceVoidCutUtils) to walls, cabinets (Casework), Generic Models,
Furniture and Specialty Equipment that a Gola channel's recess void actually cuts, and removes
cuts from elements it no longer touches.

Rules (2026-09-29, after a "circular chain of references" in the Belmont model):
- Each candidate is cut in its own transaction and kept only if it removes material, so
  elements that merely touch the channel's bounding box are left alone, and one element Revit
  refuses (for example a circular chain with the element the channel is placed on) no longer
  rolls back the others. Everything is grouped as one "Gola Auto Cut" undo step.
- Refused cuts are logged with Revit's own message and reported to the user once per element
  (a dialog from the automatic path, a list from the button) instead of Revit's generic error.
- Re-hosting a channel onto its own reference plane was tried and dropped: the API refuses
  line-based placement on reference planes ("does not coincide with the input face").

Flow: the updater sees Gola channels added or changed and queues them (Revit forbids
InstanceVoidCutUtils during a dynamic update), then raises an ExternalEvent; Revit runs
process_pending right after the user's action. The Cut Gola Recesses button calls apply()
for every channel in the model. apply() must be called outside any open transaction.
"""
import os, datetime, traceback
from Autodesk.Revit import DB
from Autodesk.Revit import UI
from System import Guid
from System.Collections.Generic import List

FAMILY_PREFIX = 'Richelieu_Gola'
UPDATER_GUID = Guid('6f4f1b8e-2d3a-4c71-9a55-0d7c3e9b8a21')
PAD_FT = 0.5 / 304.8          # 0.5 mm, so a face touching the channel box still counts as a candidate
MIN_CUT_MM3 = 1.0             # a candidate is kept only if the cut removes more than this
LOG = os.path.join(os.environ.get('TEMP', '.'), 'gola_autocut.log')
CUT_CATEGORIES = [DB.BuiltInCategory.OST_Walls, DB.BuiltInCategory.OST_Casework, DB.BuiltInCategory.OST_GenericModel,
                  DB.BuiltInCategory.OST_Furniture, DB.BuiltInCategory.OST_FurnitureSystems,
                  DB.BuiltInCategory.OST_SpecialityEquipment]

_pending = []   # (document, set of instance id values) waiting for the external event
_event = None
_warned = set()   # (document title, element id) already logged as not cuttable


def log(msg):
    with open(LOG, 'a') as f:
        f.write('%s  %s\n' % (datetime.datetime.now().isoformat(), msg))


class _Failures(DB.IFailuresPreprocessor):
    """Record every failure message; delete warnings; roll back on errors (never a modal prompt)."""
    def __init__(self):
        self.messages = []

    def PreprocessFailures(self, accessor):
        rollback = False
        for f in accessor.GetFailureMessages():
            self.messages.append('%s: %s' % (f.GetSeverity(), f.GetDescriptionText()))
            if f.GetSeverity() == DB.FailureSeverity.Warning: accessor.DeleteWarning(f)
            else: rollback = True
        return DB.FailureProcessingResult.ProceedWithRollBack if rollback else DB.FailureProcessingResult.Continue


def _start(doc, name):
    tx = DB.Transaction(doc, name)
    fp = _Failures()
    o = tx.GetFailureHandlingOptions(); o.SetFailuresPreprocessor(fp); o.SetClearAfterRollback(True)
    tx.SetFailureHandlingOptions(o); tx.Start()
    return tx, fp


def _commit(tx, fp, what, doc):
    ok = tx.Commit() == DB.TransactionStatus.Committed
    if not ok: log('%s: %s rolled back: %s' % (doc.Title, what, ' | '.join(fp.messages) or 'no message'))
    return ok


def is_gola(e):
    if not isinstance(e, DB.FamilyInstance): return False
    if not e.Symbol.Family.Name.startswith(FAMILY_PREFIX): return False
    return DB.InstanceVoidCutUtils.IsVoidInstanceCuttingElement(e)


def describe(e):
    cat = e.Category.Name if e.Category else '?'
    fam = e.Symbol.Family.Name if isinstance(e, DB.FamilyInstance) else DB.Element.Name.GetValue(e)
    return '%s %d (%s)' % (cat, e.Id.Value, fam)


def touching(doc, inst):
    """(cuttable, not_cuttable) candidates in the cut categories whose boxes touch inst's box; Gola channels excluded."""
    bb = inst.get_BoundingBox(None)
    if bb is None: return [], []
    pad = DB.XYZ(PAD_FT, PAD_FT, PAD_FT)
    cats = List[DB.BuiltInCategory](CUT_CATEGORIES)
    f = DB.BoundingBoxIntersectsFilter(DB.Outline(bb.Min.Subtract(pad), bb.Max.Add(pad)))
    ok, no = [], []
    for e in DB.FilteredElementCollector(doc).WherePasses(DB.ElementMulticategoryFilter(cats)).WhereElementIsNotElementType().WherePasses(f):
        if e.Id == inst.Id or is_gola(e): continue
        (ok if DB.InstanceVoidCutUtils.CanBeCutWithVoid(e) else no).append(e)
    return ok, no


def cut_ids(inst):
    return set(i.Value for i in DB.InstanceVoidCutUtils.GetElementsBeingCut(inst))


def _solids(geom):
    for g in geom:
        if isinstance(g, DB.Solid) and g.Volume > 1e-12: yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in _solids(g.GetInstanceGeometry()): yield s


def volume_mm3(e):
    g = e.get_Geometry(DB.Options())
    return sum(s.Volume for s in _solids(g)) * 304.8 ** 3 if g is not None else 0.0


def placed_on(doc, inst, e):
    """Diagnostic: True if inst is placed on e (face host, or its Work Plane reads "<family> : <type>" of e)."""
    if inst.Host is not None and inst.Host.Id == e.Id: return True
    if not isinstance(e, DB.FamilyInstance): return False
    wp = inst.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM)
    name = wp.AsString() if wp is not None else None
    return bool(name) and name == '%s : %s' % (e.Symbol.Family.Name, DB.Element.Name.GetValue(e.Symbol))


def apply(doc, insts):
    """Make each channel cut exactly the candidates its void really cuts. Call outside any transaction.
    Returns rows [instance id, added ids, removed ids, not-cuttable descriptions, refused [description, reason]]."""
    done = []
    tg = DB.TransactionGroup(doc, 'Gola Auto Cut'); tg.Start()
    changed = False
    for inst in insts:
        if inst is None or not inst.IsValidObject or not is_gola(inst): continue
        ok, no = touching(doc, inst)
        want = dict((e.Id.Value, e) for e in ok)
        have = cut_ids(inst)
        added, removed, refused = [], [], []
        for eid in have:
            if eid in want: continue
            e = doc.GetElement(DB.ElementId(eid))
            if e is None: continue
            tx, fp = _start(doc, 'Gola uncut')
            DB.InstanceVoidCutUtils.RemoveInstanceVoidCut(doc, e, inst)
            if _commit(tx, fp, 'uncutting %s' % describe(e), doc): removed.append(eid); changed = True
        for eid, e in want.items():
            if eid in have: continue
            before = volume_mm3(e)
            tx, fp = _start(doc, 'Gola cut')
            DB.InstanceVoidCutUtils.AddInstanceVoidCut(doc, e, inst)
            doc.Regenerate()
            if before - volume_mm3(e) <= MIN_CUT_MM3:
                tx.RollBack()          # touches the box only; the void removes nothing from it
                continue
            if _commit(tx, fp, 'cutting %s with Gola %d' % (describe(e), inst.Id.Value), doc):
                added.append(eid); changed = True
            else:
                why = ' | '.join(fp.messages) or 'rolled back without a message'
                if placed_on(doc, inst, e): why += ' (the channel is placed on this element)'
                refused.append([describe(e), why])
        blocked = []
        for e in no:
            blocked.append(describe(e))
            key = (doc.Title, e.Id.Value)
            if key not in _warned:
                _warned.add(key)
                log('%s: %s touches Gola %d but Revit does not allow it to be cut by voids' % (doc.Title, describe(e), inst.Id.Value))
        if added or removed:
            log('%s: Gola %d cut +%s -%s' % (doc.Title, inst.Id.Value, added, removed))
        done.append([inst.Id.Value, added, removed, blocked, refused])
    if changed: tg.Assimilate()
    else: tg.RollBack()
    return done


def gola_instances(doc):
    return [e for e in DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance) if is_gola(e)]


_reported = set()   # (document title, instance id, refused element) already shown to the user


def process_pending():
    """Apply queued cuts per document; tell the user once about each cut Revit refused."""
    jobs = list(_pending); del _pending[:]
    done = []
    for doc, ids in jobs:
        if not doc.IsValidObject or doc.IsReadOnly: continue
        insts = [doc.GetElement(DB.ElementId(i)) for i in ids]
        rows = apply(doc, [e for e in insts if e is not None])
        done.extend(rows)
        new = []
        for r in rows:
            for desc, why in r[4]:
                key = (doc.Title, r[0], desc)
                if key not in _reported:
                    _reported.add(key); new.append('Gola %d could not cut %s:\n%s' % (r[0], desc, why))
        if new and _event is not None:
            UI.TaskDialog.Show('Gola Auto Cut', '\n\n'.join(new) + '\n\nOther cuts were applied. Details: ' + LOG)
    return done


class _CutHandler(UI.IExternalEventHandler):
    def Execute(self, uiapp):
        try:
            process_pending()
        except Exception:
            log('process_pending FAILED\n%s' % traceback.format_exc())

    def GetName(self): return 'Gola Auto Cut'


class GolaAutoCutUpdater(DB.IUpdater):
    def __init__(self, addin_id):
        self._id = DB.UpdaterId(addin_id, UPDATER_GUID)

    def GetUpdaterId(self): return self._id
    def GetUpdaterName(self): return 'Gola Auto Cut'
    def GetAdditionalInformation(self): return 'Cuts walls and cabinets with the recess void of Richelieu Gola channels when they are placed or changed.'
    def GetChangePriority(self): return DB.ChangePriority.FloorsRoofsStructuralWalls

    def Execute(self, data):
        doc = data.GetDocument()
        try:
            ids = set(i.Value for i in list(data.GetAddedElementIds()) + list(data.GetModifiedElementIds())
                      if is_gola(doc.GetElement(i)))
            if ids:
                _pending.append((doc, ids))
                if _event is not None: _event.Raise()
        except Exception:
            # Recorded, not swallowed: an exception here would make Revit disable the updater for the session.
            log('%s: updater FAILED\n%s' % (doc.Title, traceback.format_exc()))


def register(addin_id, with_event=True):
    """(Re)register the updater and its triggers for all documents. Returns the updater.
    with_event=False (tests only) leaves the queue to be flushed by calling process_pending()."""
    global _event
    if with_event and _event is None:
        _event = UI.ExternalEvent.Create(_CutHandler())
    updater = GolaAutoCutUpdater(addin_id)
    uid = updater.GetUpdaterId()
    if DB.UpdaterRegistry.IsUpdaterRegistered(uid):
        DB.UpdaterRegistry.UnregisterUpdater(uid)
    DB.UpdaterRegistry.RegisterUpdater(updater, True)  # optional: models open fine without this extension
    f = DB.LogicalAndFilter(DB.ElementClassFilter(DB.FamilyInstance), DB.ElementCategoryFilter(DB.BuiltInCategory.OST_GenericModel))
    DB.UpdaterRegistry.AddTrigger(uid, f, DB.Element.GetChangeTypeElementAddition())
    DB.UpdaterRegistry.AddTrigger(uid, f, DB.Element.GetChangeTypeGeometry())
    log('Gola Auto Cut updater registered')
    return updater


def unregister(addin_id):
    uid = DB.UpdaterId(addin_id, UPDATER_GUID)
    if DB.UpdaterRegistry.IsUpdaterRegistered(uid):
        DB.UpdaterRegistry.UnregisterUpdater(uid)

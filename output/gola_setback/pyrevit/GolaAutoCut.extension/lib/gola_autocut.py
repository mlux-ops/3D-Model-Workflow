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
- 2026-10-02: Revit cannot cut an in-place family with a channel placed on a face of that same
  element (circular chain: type -> instance -> in-place form -> channel). Such a channel is
  replaced by an identical copy on the level below (detach); its Plane Faces Up parameter keeps
  the profile the same way up. Verified on the Belmont in-place Countertop80 (rolled-back test).

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


def _in_place(e):
    return isinstance(e, DB.FamilyInstance) and e.Symbol.Family.IsInPlace


def _level_below(doc, z):
    levels = sorted(DB.FilteredElementCollector(doc).OfClass(DB.Level), key=lambda l: l.Elevation)
    below = [l for l in levels if l.Elevation <= z + 1e-6]
    return below[-1] if below else levels[0]


def _box(e):
    """Extents (mm) of e's visible solids. The element bounding box is not used: it includes void forms."""
    ps = [p for s in _solids(e.get_Geometry(DB.Options())) for ed in s.Edges for p in ed.Tessellate()]
    return [min(p.X for p in ps) * 304.8, min(p.Y for p in ps) * 304.8, min(p.Z for p in ps) * 304.8,
            max(p.X for p in ps) * 304.8, max(p.Y for p in ps) * 304.8, max(p.Z for p in ps) * 304.8]


_KEEP_BUILTINS = (DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS, DB.BuiltInParameter.ALL_MODEL_MARK)


def detach(doc, inst, why):
    """Replace a face-placed channel by an identical copy on the level below it (no face, no work plane on
    the element), so it can cut that element. Needs the family's 'Plane Faces Up' parameter. A face facing
    down (or up) maps to the level frame by toggling Flip Profile and Plane Faces Up (down) or keeping them
    (up). Returns (new instance or None, message). Runs its own transaction; call inside apply's group."""
    if inst.LookupParameter('Plane Faces Up') is None or inst.LookupParameter('Flip Profile') is None:
        return None, 'family has no Plane Faces Up parameter (reload the current Gola family)'
    bz = inst.GetTransform().BasisZ.Z
    if abs(bz) < 0.99:
        return None, 'the channel is on a vertical face; place it on the underside instead'
    c = inst.Location.Curve
    before_box, before_vol = _box(inst), volume_mm3(inst)
    tx, fp = _start(doc, 'Gola detach from in-place element')
    lev = _level_below(doc, min(c.GetEndPoint(0).Z, c.GetEndPoint(1).Z))
    new = doc.Create.NewFamilyInstance(c, inst.Symbol, lev, DB.Structure.StructuralType.NonStructural)
    doc.Regenerate()
    dz = c.GetEndPoint(0).Z - new.Location.Curve.GetEndPoint(0).Z   # level placement drops the line onto the level
    if abs(dz) > 1e-9: DB.ElementTransformUtils.MoveElement(doc, new.Id, DB.XYZ(0, 0, dz))
    for p in inst.Parameters:
        if p.IsReadOnly or p.StorageType == getattr(DB.StorageType, 'None'): continue
        name = p.Definition.Name
        if name in ('Flip Profile', 'Plane Faces Up'): continue
        bip = p.Definition.BuiltInParameter if isinstance(p.Definition, DB.InternalDefinition) else DB.BuiltInParameter.INVALID
        if bip != DB.BuiltInParameter.INVALID and bip not in _KEEP_BUILTINS: continue
        q = new.get_Parameter(bip) if bip != DB.BuiltInParameter.INVALID else new.LookupParameter(name)
        if q is None or q.IsReadOnly: continue
        if p.StorageType == DB.StorageType.Double: q.Set(p.AsDouble())
        elif p.StorageType == DB.StorageType.Integer: q.Set(p.AsInteger())
        elif p.StorageType == DB.StorageType.String: q.Set(p.AsString() or '')
        elif p.StorageType == DB.StorageType.ElementId: q.Set(p.AsElementId())
    flip = inst.LookupParameter('Flip Profile').AsInteger()
    up = inst.LookupParameter('Plane Faces Up').AsInteger()
    if bz < 0: flip, up = 1 - flip, 1 - up
    new.LookupParameter('Flip Profile').Set(flip)
    new.LookupParameter('Plane Faces Up').Set(up)
    doc.Regenerate()
    after_box, after_vol = _box(new), volume_mm3(new)
    if max(abs(a - b) for a, b in zip(before_box, after_box)) > 0.05 or abs(after_vol - before_vol) > 1e-3 * max(before_vol, 1):
        tx.RollBack()
        return None, 'the unhosted copy did not match the original (box %s vs %s); left as it was' % (
            [round(v, 2) for v in before_box], [round(v, 2) for v in after_box])
    old_id = inst.Id.Value
    doc.Delete(inst.Id)
    if not _commit(tx, fp, 'detaching Gola %d' % old_id, doc):
        return None, 'Revit refused the replacement: ' + (' | '.join(fp.messages) or 'no message')
    log('%s: Gola %d replaced by %d on level %s (%s)' % (doc.Title, old_id, new.Id.Value, lev.Name, why))
    return new, 'Gola %d replaced by %d, unhosted on level %s (%s)' % (old_id, new.Id.Value, lev.Name, why)


def _detach_reason(doc, inst, ok, detach_all):
    """Why inst must leave the element it sits on before cutting, or None. Revit cannot cut an in-place
    family with a channel placed on that same element (circular chain of references; seen on the
    in-place Countertop80 in the Belmont model, 2026-10-02). detach_all (tests) treats any element as in-place."""
    if isinstance(inst.Host, DB.Level): return None
    for e in ok:
        if (detach_all or _in_place(e)) and placed_on(doc, inst, e):
            return 'placed on in-place element %s' % describe(e)
    if _in_place(inst.Host): return 'placed on in-place element %s' % describe(inst.Host)
    return None


def apply(doc, insts, detach_all=False):
    """Make each channel cut exactly the candidates its void really cuts. Call outside any transaction.
    Returns rows [instance id, added ids, removed ids, not-cuttable descriptions, refused [description, reason],
    replacement message or None]. A channel placed on an in-place element is first replaced by an
    unhosted copy (detach), and the row's id is the new instance's."""
    done = []
    tg = DB.TransactionGroup(doc, 'Gola Auto Cut'); tg.Start()
    changed = False
    for inst in insts:
        if inst is None or not inst.IsValidObject or not is_gola(inst): continue
        ok, no = touching(doc, inst)
        note = None
        replaced = False
        why = _detach_reason(doc, inst, ok, detach_all)
        if why:
            new, note = detach(doc, inst, why)
            if new is not None:
                inst = new; changed = True; replaced = True
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
        if note and not replaced: refused.append(['(replacement)', note])
        done.append([inst.Id.Value, added, removed, blocked, refused, note])
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

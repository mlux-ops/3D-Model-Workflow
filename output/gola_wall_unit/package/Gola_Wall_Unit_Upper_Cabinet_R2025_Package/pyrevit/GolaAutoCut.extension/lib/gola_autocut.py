# -*- coding: utf-8 -*-
"""Automatic wall cuts for Richelieu Gola two-click (line-based) families.

Revit only auto-cuts hosts with voids for face- and wall-based templates. The Gola families
are line based (two-click placement), so this module applies the same cut Revit's
Cut Geometry makes (InstanceVoidCutUtils) to every wall, cabinet (Casework), Generic Model,
Furniture or Specialty Equipment element a Gola channel's bounding box touches, and removes
cuts from elements it no longer touches. A loadable family can only be cut if its own
"Cut with Voids When Loaded" is on; touching elements that cannot be cut are logged.

Flow: the updater sees Gola channels added or changed and queues them (Revit forbids
InstanceVoidCutUtils during a dynamic update), then raises an ExternalEvent; Revit runs
process_pending right after the user's action, as its own "Gola Auto Cut" undo step.
The Cut Gola Recesses button calls sync() directly for every channel in the model.
"""
import os, datetime, traceback
from Autodesk.Revit import DB
from Autodesk.Revit import UI
from System import Guid
from System.Collections.Generic import List

FAMILY_PREFIX = 'Richelieu_Gola'
UPDATER_GUID = Guid('6f4f1b8e-2d3a-4c71-9a55-0d7c3e9b8a21')
PAD_FT = 0.5 / 304.8  # 0.5 mm, so a wall face touching the channel box still counts
LOG = os.path.join(os.environ.get('TEMP', '.'), 'gola_autocut.log')

_pending = []   # (document, set of instance id values) waiting for the external event
_event = None


def log(msg):
    with open(LOG, 'a') as f:
        f.write('%s  %s\n' % (datetime.datetime.now().isoformat(), msg))


def is_gola(e):
    if not isinstance(e, DB.FamilyInstance): return False
    if not e.Symbol.Family.Name.startswith(FAMILY_PREFIX): return False
    return DB.InstanceVoidCutUtils.IsVoidInstanceCuttingElement(e)


CUT_CATEGORIES = [DB.BuiltInCategory.OST_Walls, DB.BuiltInCategory.OST_Casework, DB.BuiltInCategory.OST_GenericModel,
                  DB.BuiltInCategory.OST_Furniture, DB.BuiltInCategory.OST_FurnitureSystems,
                  DB.BuiltInCategory.OST_SpecialityEquipment]
_warned = set()   # (document title, element id) already logged as not cuttable


def touching(doc, inst):
    """(cuttable, not_cuttable) elements in the cut categories whose boxes touch inst's box; Gola channels excluded."""
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


def needs_change(doc, inst):
    return set(e.Id.Value for e in touching(doc, inst)[0]) != cut_ids(inst)


def describe(e):
    cat = e.Category.Name if e.Category else '?'
    fam = e.Symbol.Family.Name if isinstance(e, DB.FamilyInstance) else DB.Element.Name.GetValue(e)
    return '%s %d (%s)' % (cat, e.Id.Value, fam)


def sync(doc, inst):
    """Make the set of elements cut by inst equal the cuttable elements it touches.
    Returns (added, removed, not_cuttable) lists. Must run inside an open transaction, outside a dynamic update."""
    ok, no = touching(doc, inst)
    want = dict((e.Id.Value, e) for e in ok)
    have = cut_ids(inst)
    added, removed = [], []
    for eid, e in want.items():
        if eid not in have:
            DB.InstanceVoidCutUtils.AddInstanceVoidCut(doc, e, inst); added.append(eid)
    for eid in have:
        if eid in want: continue
        e = doc.GetElement(DB.ElementId(eid))
        if e is not None:
            DB.InstanceVoidCutUtils.RemoveInstanceVoidCut(doc, e, inst); removed.append(eid)
    blocked = []
    for e in no:
        blocked.append(describe(e))
        key = (doc.Title, e.Id.Value)
        if key not in _warned:
            _warned.add(key)
            log('%s: %s touches Gola %d but cannot be cut - turn on "Cut with Voids When Loaded" in its family'
                % (doc.Title, describe(e), inst.Id.Value))
    return added, removed, blocked


def gola_instances(doc):
    return [e for e in DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance) if is_gola(e)]


def process_pending():
    """Apply queued cuts, one transaction per document, only when something changes."""
    jobs = list(_pending); del _pending[:]
    done = []
    for doc, ids in jobs:
        if not doc.IsValidObject or doc.IsReadOnly: continue
        insts = [doc.GetElement(DB.ElementId(i)) for i in ids]
        insts = [e for e in insts if e is not None and is_gola(e) and needs_change(doc, e)]
        if not insts: continue
        tx = DB.Transaction(doc, 'Gola Auto Cut'); tx.Start()
        for e in insts:
            added, removed, _ = sync(doc, e)
            done.append([e.Id.Value, added, removed])
            log('%s: instance %d cut +%s -%s' % (doc.Title, e.Id.Value, added, removed))
        if tx.Commit() != DB.TransactionStatus.Committed:
            log('%s: Gola Auto Cut transaction did not commit' % doc.Title)
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

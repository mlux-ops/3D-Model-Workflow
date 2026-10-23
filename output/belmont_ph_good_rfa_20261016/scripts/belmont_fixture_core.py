# -*- coding: utf-8 -*-
"""Shared Revit 2025 native family builder; executed only inside an authorized Revit runner.

Length inputs in inches. The established runner supplies APP, DB, JOB, TARGET_RFA,
progress and result to the fixture-specific entry script.
"""
import os
import math
from System.Collections.Generic import List

TEMPLATE_ROOT = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial'


def xyz(DB, x=0, y=0, z=0):
    return DB.XYZ(float(x)/12.0, float(y)/12.0, float(z)/12.0)


def ring(DB, center, radius):
    loop = DB.CurveLoop()
    loop.Append(DB.Arc.Create(center, radius/12.0, 0, math.pi, DB.XYZ.BasisX, DB.XYZ.BasisY))
    loop.Append(DB.Arc.Create(center, radius/12.0, math.pi, 2*math.pi, DB.XYZ.BasisX, DB.XYZ.BasisY))
    return loop


def rectangle(DB, x0, y0, x1, y1, z):
    points = [xyz(DB,x0,y0,z),xyz(DB,x1,y0,z),xyz(DB,x1,y1,z),xyz(DB,x0,y1,z)]
    loop = DB.CurveLoop()
    for i in range(4):
        loop.Append(DB.Line.CreateBound(points[i], points[(i+1)%4]))
    return loop


class NativeBuild(object):
    def __init__(self, app, DB, target, model, manufacturer, variant, host, source, notes):
        self.app, self.DB, self.target, self.host = app, DB, target, host
        self.docs = []
        self.parts = []
        self.material_params = {}
        template = os.path.join(TEMPLATE_ROOT, 'Generic Model face based.rft')
        if str(app.VersionNumber) != '2025':
            raise RuntimeError('Revit 2025 required; found '+str(app.VersionNumber))
        if not os.path.isfile(template):
            raise RuntimeError('Face-based template missing: '+template)
        if os.path.isfile(target):
            raise RuntimeError('Target exists, choose an unused release filename: '+target)
        self.doc = app.NewFamilyDocument(template)
        self.docs.append(self.doc)
        self.tx = DB.Transaction(self.doc,'Native family '+model)
        self.tx.Start()
        self.doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(self.doc,DB.BuiltInCategory.OST_LightingFixtures)
        av = self.doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL)
        if av is not None and not av.IsReadOnly: av.Set(0)
        self.fm = self.doc.FamilyManager
        self.fm.NewType(model+' - '+variant)
        for bip,value in [(DB.BuiltInParameter.ALL_MODEL_MANUFACTURER,manufacturer),
                          (DB.BuiltInParameter.ALL_MODEL_MODEL,model),
                          (DB.BuiltInParameter.ALL_MODEL_DESCRIPTION,variant+'; '+notes)]:
            p = self.fm.get_Parameter(bip)
            if p is not None and not p.IsReadOnly: self.fm.Set(p,value)
        self.text('Source URL',source)
        self.text('Model Accuracy Notes',notes)
        self.text('Retailer SKU',model)

    def text(self,name,value):
        p = self.fm.AddParameter(name,self.DB.GroupTypeId.IdentityData,self.DB.SpecTypeId.String.Text,False)
        self.fm.Set(p,str(value))
        return p

    def size(self,name,value):
        p = self.fm.AddParameter(name,self.DB.GroupTypeId.Geometry,self.DB.SpecTypeId.Length,False)
        self.fm.SetFormula(p,str(float(value))+' in')
        return p

    def material(self,name,rgb,transparency=0):
        DB=self.DB
        mat=self.doc.GetElement(DB.Material.Create(self.doc,name))
        mat.Color=DB.Color(*rgb)
        mat.Transparency=int(transparency)
        param=self.fm.AddParameter(name+' Material',DB.GroupTypeId.Materials,DB.SpecTypeId.Reference.Material,False)
        self.fm.Set(param,mat.Id)
        self.material_params[name]=param
        return param

    def part(self,name,solid,mat):
        DB=self.DB
        e=DB.FreeFormElement.Create(self.doc,solid)
        self.fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),mat)
        p=e.LookupParameter('Comments')
        if p and not p.IsReadOnly:p.Set(name)
        self.parts.append(e)
        return e

    def box(self,name,extents,mat):
        x0,y0,z0,x1,y1,z1=extents
        DB=self.DB
        solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([rectangle(DB,x0,y0,x1,y1,z0)]),DB.XYZ.BasisZ,(z1-z0)/12.0)
        return self.part(name,solid,mat)

    def cylinder(self,name,x,y,z,r,h,mat):
        DB=self.DB
        solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([ring(DB,xyz(DB,x,y,z),r)]),DB.XYZ.BasisZ,h/12.0)
        return self.part(name,solid,mat)

    def finish(self):
        DB=self.DB
        self.doc.Regenerate()
        opts=DB.Options(); opts.DetailLevel=DB.ViewDetailLevel.Fine
        points=[]
        for e in self.parts:
            for solid in e.get_Geometry(opts):
                if isinstance(solid,DB.Solid) and solid.Volume>1e-12:
                    for face in solid.Faces:
                        points.extend(face.Triangulate(1.0).Vertices)
                    for edge in solid.Edges:
                        curve=edge.AsCurve()
                        count=96 if not isinstance(curve,DB.Line) else 1
                        points.extend(curve.Evaluate(float(i)/count,True) for i in range(count+1))
        if not points:raise RuntimeError('No native solid geometry available for measurement')
        dims=[(max(getattr(p,axis) for p in points)-min(getattr(p,axis) for p in points))*12.0 for axis in 'XYZ']
        self.tx.Commit();self.tx=None
        out_dir=os.path.dirname(self.target)
        if not os.path.isdir(out_dir):os.makedirs(out_dir)
        opts=DB.SaveAsOptions();opts.MaximumBackups=1;opts.OverwriteExistingFile=False
        self.doc.SaveAs(self.target,opts)
        self.doc.Close(False);self.docs.remove(self.doc)
        return {'rfa_path':self.target,'geometry_dimensions_in':dims,
                'part_count':len(self.parts),'material_parameters':sorted(self.material_params.keys()),
                'category':'Lighting Fixtures','hosting':'face based / WorkPlaneBased',
                'revit_version':'2025','status':'SAVED_PENDING_INDEPENDENT_NATIVE_QA'}

    def close(self):
        if getattr(self,'tx',None) is not None:
            try:self.tx.RollBack()
            except Exception:pass
            self.tx=None
        for doc in reversed(self.docs):
            try:doc.Close(False)
            except Exception:pass

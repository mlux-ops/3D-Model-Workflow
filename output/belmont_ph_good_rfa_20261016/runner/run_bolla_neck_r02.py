# -*- coding: utf-8 -*-
"""Inject audited Revit context without modifying source converter."""
SCRIPT=r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\build_bolla_pd3106_bg_neck_r02.py'
scope={'__name__':'__main__','__file__':SCRIPT,'__revit__':__revit__}
execfile(SCRIPT,scope)

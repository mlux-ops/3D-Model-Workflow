# -*- coding: utf-8 -*-
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
execfile(os.path.join(ROOT, '_tools', 'build_dimple_current.py'))

# -*- coding: utf-8 -*-
"""Register the Gola Auto Cut updater each time pyRevit loads."""
from pyrevit import HOST_APP
import gola_autocut

gola_autocut.register(HOST_APP.addin_id)

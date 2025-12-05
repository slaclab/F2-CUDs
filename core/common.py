# common methods/subclasses for FACET-II CUDs


from os import path
from functools import partial
from epics import caput, PV
# random helpers ...

import yaml
SELF_PATH = path.dirname(path.abspath(__file__))
REPO_ROOT = path.join(*path.split(SELF_PATH)[:-1])
DIR_CONFIG = path.join(SELF_PATH, 'config')
with open(path.join(REPO_ROOT, 'core', 'config.yaml'), 'r') as f:
    CONFIG = yaml.safe_load(f)


def CUD_IDs(): return CONFIG['CUD_IDs']

def CUD_desc(CUD_ID): return CONFIG[CUD_ID]['desc']

def CUD_ID(CUD_desc):
    for k,v in CONFIG.items():
        if k not in CONFIG['CUD_IDs']: continue
        if v['desc'] == CUD_desc: return k

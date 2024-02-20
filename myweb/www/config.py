from typing import Any
import config_default,config_override
class Dict(dict):
    def __init__(self,names=(),values=(),**kw):
        super().__init__(**kw)
        for k,v in zip(names,values):
            self[k] = v
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)
    def __setattr__(self, __name: str, __value: Any) -> None:
        self[__name] = __value
def merge(defaults,override):
    r ={}
    for k,v in defaults.items():
        if k in override:
            if isinstance(v,dict):
                r[k] = merge(v,override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d):
    D = Dict()
    for k,v in d.items():
        D[k] = toDict(v) if isinstance(v,dict) else v
    return D

try:
    configs = merge(config_default.configs,config_override.configs)
except Exception  as e:
    pass

configs = toDict(configs)

from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec
from sys import modules
from types import ModuleType, new_class


def make_fake_module(name: str) -> ModuleType:
    return module_from_spec(ModuleSpec(name, None))


# six
six = make_fake_module("six")
six.PY2 = False  # type:ignore[attr-defined]
modules["six"] = six

# tqdm
tqdm_auto = make_fake_module("tqdm.auto")
tqdm_auto.tqdm = new_class("tqdm")  # type:ignore[attr-defined]
modules["tqdm.auto"] = tqdm_auto


# pyopenjtalk.htsengine
class HTSEngine:
    def __init__(self, voice: bytes):
        pass


htsengine = make_fake_module("pyopenjtalk.htsengine")
htsengine.HTSEngine = HTSEngine  # type:ignore[attr-defined]
modules["pyopenjtalk.htsengine"] = htsengine

# hook-pyopenjtalk.pyでpyopenjtalk.htsengineを除外したこのままだとImportErrorが発生する  # noqa: D100
# これを防ぐため実行時フックで偽のモジュールを作成して予めimportしておく
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec
from sys import modules


class HTSEngine:  # noqa: D101
    def __init__(self, voice: bytes):
        pass


htsengine = module_from_spec(ModuleSpec("pyopenjtalk.htsengine", None))
htsengine.HTSEngine = HTSEngine  # type:ignore[attr-defined]
modules["pyopenjtalk.htsengine"] = htsengine

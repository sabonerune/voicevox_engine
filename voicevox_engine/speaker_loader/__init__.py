from ..utility.path_utility import engine_root
from . import builtin_speaker, speaker

builtin_dir = engine_root() / "resources/buitin_speaker"


def load_speakers(builtin_dir=builtin_dir) -> speaker.Speakers:
    return builtin_speaker.load_builtin_config(builtin_dir)

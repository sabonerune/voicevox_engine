from pathlib import Path

import pytest

from voicevox_engine.speaker_loader import builtin_speaker, speaker

BUILTIN_DIR = Path("resources/buitin_speaker")


@pytest.fixture
def speakers():
    return builtin_speaker.load_buitin_config(BUILTIN_DIR)


def test_load_builtin_speaker(speakers: speaker.Speakers):
    for _speaker in speakers.speakers:
        assert _speaker is speakers.speaker(_speaker.speaker_id)
        assert _speaker.speaker_portrait.exists()
        assert _speaker.speaker_policy.exists()
        for style in _speaker.styles:
            assert style is speakers.style(style.style_id)
            assert style.htsvoice.exists()
            assert style.icon.exists()
            assert style.portrait is None or style.portrait.exists()
            for sample in style.samples:
                assert sample.exists()

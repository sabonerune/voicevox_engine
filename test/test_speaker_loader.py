import base64
from pathlib import Path

from voicevox_engine import speaker_loader

TEST_SPEAKER = {
    "style_name": "テスト",
    "style_name": "テスト",
    "style_id": 255,
    "htsvoice": Path("resources/buitin_speaker/mei/0/mei_normal.htsvoice"),
    "icon": Path("resources/buitin_speaker/mei/0/mei_normal.png"),
    "portrait": Path("resources/buitin_speaker/mei/portrait.png"),
    "samples": [Path("resources/buitin_speaker/mei/0/mei_normal_sample_001.wav")],
    "config": {},
}

TEST_STYLE = {
    "speaker_name": "テスト",
    "speaker_id": "テスト",
    "speaker_portrait": Path("resources/buitin_speaker/mei/portrait.png"),
    "speaker_policy": Path("resources/buitin_speaker/mei/COPYRIGHT.txt"),
}


def test_style_info():
    info = speaker_loader.speaker.Style(**TEST_SPEAKER).info
    assert base64.b64decode(info.icon) == TEST_SPEAKER["icon"].read_bytes()
    assert base64.b64decode(info.portrait) == TEST_SPEAKER["portrait"].read_bytes()
    for i, sample in enumerate(info.voice_samples):
        assert base64.b64decode(sample) == TEST_SPEAKER["samples"][i].read_bytes()


def test_speaker_info():
    styles = [speaker_loader.speaker.Style(**TEST_SPEAKER)]
    info = speaker_loader.speaker.Speaker(**TEST_STYLE, styles=styles).speaker_info
    assert (
        base64.b64decode(info.portrait) == TEST_STYLE["speaker_portrait"].read_bytes()
    )
    # assert info.policy == TEST_STYLE["speaker_policy"].read_text("utf-8")
    assert info.style_infos == [i.info for i in styles]

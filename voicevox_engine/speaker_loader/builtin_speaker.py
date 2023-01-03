from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from voicevox_engine.speaker_loader.speaker import Speaker, Speakers, Style, VoiceConfig


class BuiltinStyleRefModel(BaseModel):
    style_id: int
    style_name: str


class BuiltinSpeakerConfigModel(BaseModel):
    speaker_name: str
    speaker_id: str
    styles: List[BuiltinStyleRefModel]
    speaker_portrait: str
    speaker_policy: str


class BuiltinStyleConfigModel(BaseModel):
    htsvoice: str
    style_portrait: Optional[str]
    icon: str
    samples: List[str]
    config: VoiceConfig


def load_buitin_config(builtin_dir: Path):
    config_files = builtin_dir.glob("*/htsvoice-package.json")
    speakers: Dict[str, Speakers] = {}
    for i in config_files:
        config_dir = i.parent
        speaker_config = BuiltinSpeakerConfigModel.parse_file(i)
        styles: List[Style] = []
        for j in speaker_config.styles:
            style_dir = config_dir / str(j.style_id)
            style_config = BuiltinStyleConfigModel.parse_file(style_dir / "config.json")
            samples = [style_dir / i for i in style_config.samples]
            style = Style(
                style_name=j.style_name,
                style_id=j.style_id,
                htsvoice=style_dir / style_config.htsvoice,
                icon=style_dir / style_config.icon,
                portrait=None
                if style_config.style_portrait is None
                else style_dir / style_config.style_portrait,
                samples=samples,
            )
            styles.append(style)
        speakers[speaker_config.speaker_id] = Speaker(
            speaker_name=speaker_config.speaker_name,
            speaker_id=speaker_config.speaker_id,
            speaker_portrait=config_dir / speaker_config.speaker_portrait,
            speaker_policy=config_dir / speaker_config.speaker_policy,
            styles=styles,
        )
    return Speakers(_speakers=speakers)

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from voicevox_engine.metas import Metas


class VoiceConfig(BaseModel):
    half_tone_multiplier: Optional[float]
    speed_multiplier: Optional[float]
    volume_multiplie: Optional[float]


def b64encode_str(s):
    return base64.b64encode(s).decode("utf-8")


@dataclass
class Style:
    style_name: str
    style_id: int
    htsvoice: Path
    icon: Path
    portrait: Optional[Path]
    samples: List[Path]

    @property
    def speaker_style(self):
        return Metas.SpeakerStyle(name=self.style_name, id=self.style_id)

    @property
    def info(self):
        icon_str = b64encode_str(self.icon.read_bytes())
        if self.portrait:
            portrait_str = b64encode_str(self.portrait.read_bytes())
        else:
            portrait_str = None
        samples_str = [b64encode_str(i.read_bytes()) for i in self.samples]
        return Metas.StyleInfo(
            id=self.style_id,
            icon=icon_str,
            portrait=portrait_str,
            voice_samples=samples_str,
        )


@dataclass
class Speaker:
    speaker_name: str
    speaker_id: str
    speaker_portrait: Path
    speaker_policy: Path
    styles: List[Style]

    @property
    def speaker(self):
        return Metas.Speaker(
            name=self.speaker_name,
            speaker_uuid=self.speaker_id,
            styles=[i.speaker_style for i in self.styles],
            version="0.0.0",
        )

    @property
    def speaker_info(self):
        policy_str = self.speaker_policy.read_text(encoding="utf-8")
        if self.speaker_policy.suffix == ".txt":
            policy_str = "<pre>" + policy_str + "</pre>"
        portrait_str = b64encode_str(self.speaker_portrait.read_bytes())
        return Metas.SpeakerInfo(
            policy=policy_str,
            portrait=portrait_str,
            style_infos=[i.info for i in self.styles],
        )


@dataclass
class Speakers:
    _speakers: Dict[str, Speaker]

    @property
    def speakers(self):
        return [i for i in self._speakers.values()]

    @property
    def speaker_meta(self):
        return [i.speaker for i in self.speakers]

    def style(self, style_id: str):
        speakers = self._speakers.values()
        for i in speakers:
            for j in i.styles:
                if j.style_id == style_id:
                    return j
        return None

    def speaker(self, speaker_id: str):
        speaker = self._speakers.get(speaker_id)
        if speaker is None:
            return None
        return speaker

    def speakerInfo(self, speaker_id: str):
        speaker = self._speakers.get(speaker_id)
        if speaker is None:
            return None
        return speaker.speaker_info

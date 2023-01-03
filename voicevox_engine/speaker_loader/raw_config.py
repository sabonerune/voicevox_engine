import hashlib
import json
import uuid
from pathlib import Path
from typing import Final, List, Optional, Union

from pydantic import BaseModel, Field, conint, constr

from ..engine_manifest import EngineManifestLoader
from ..utility.path_utility import engine_root
from .speaker import Speaker, Style, VoiceConfig

# JS_MAX_SAFE_INTEGERはSAPIForVOICEVOXの上限がC#のint型なので互換性上使えない
# YMM4も恐らく同様
JS_MAX_SAFE_INTEGER: Final[int] = 2**53 - 1
MAX_STYLE_ID: Final[int] = 2**31 - 1
MIN_STYLE_ID: Final[int] = 256
JS_MIN_SAFE_INTEGER: Final[int] = -(2**53 - 1)

root_dir = engine_root()
manifest = EngineManifestLoader(
    root_dir / "engine_manifest.json", root_dir
).load_manifest()


class RawHtsVoiceConfig(BaseModel):
    speaker_name: Optional[str]
    style_name: str = Field(default="ノーマル")
    htsvoice: str
    portrait: Optional[str]
    icon: Optional[str]
    samples: Optional[List[str]]
    hidden: Optional[bool] = Field(default=False)
    config: Optional[VoiceConfig]
    speaker_id: Optional[
        constr(
            regex="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"  # noqa: B950, F722
        )
    ]
    style_id: Union[
        conint(ge=MIN_STYLE_ID, le=JS_MAX_SAFE_INTEGER),
        conint(ge=JS_MAX_SAFE_INTEGER, le=JS_MIN_SAFE_INTEGER),
    ]
    priority: Optional[conint(ge=0)]


class HtsvoiceFileInfo:
    def __init__(self, htsvoice_path: Path, config_dir: Path, namespace: str) -> None:
        self.htsvoice_file = htsvoice_path
        self.config_dir = config_dir
        self.namespace = namespace

    @property
    def digest(self) -> bytes:
        return hashlib.sha512(self.htsvoice_file.read_bytes()).digest()

    @property
    def speaker_name(self):
        return self.htsvoice_file.stem

    @property
    def config_name(self):
        return f"{self.speaker_name}_htsvoice"

    @property
    def current_config_dir(self):
        return self.config_dir / self.config_name

    @property
    def config_file(self):
        return self.current_config_dir / f"{self.config_name}.json"

    @property
    def speaker_id(self):
        return str(uuid.uuid5(uuid.UUID(self.namespace), self.digest.hex()))

    @property
    def style_id(self):
        return (
            int.from_bytes(self.digest, byteorder="big", signed=False)
            % (MAX_STYLE_ID - MIN_STYLE_ID)
            + MIN_STYLE_ID
        )


def load_htsvoice_config(info: HtsvoiceFileInfo):
    config_path = info.config_file
    data: dict = json.load(config_path.open("rb"))
    config = RawHtsVoiceConfig.parse_obj(data)
    return config


def load_raw_htsvoice(htsvoice_dir: Path):
    speakers: dict[str, list[RawHtsVoiceConfig]] = {}
    config_dir = htsvoice_dir / "config"
    htsvoices = htsvoice_dir.glob("*.htsvoice")
    auto_priority = 0
    for i in htsvoices:
        info = HtsvoiceFileInfo(i, config_dir, manifest.uuid)
        config = load_htsvoice_config(info)
        if config.hidden:
            continue
        if config.priority is None:
            auto_priority += 1
            config.priority = auto_priority
        else:
            config.priority *= -1
        styles: list = speakers.setdefault(info.speaker_id, [])
        styles.append(config)
    styles = {}
    for speaker_id, info in speakers.items():
        info.sort(key=lambda x: x.priority, reverse=True)
        s = Speaker(
            speaker_name=info[0],
            speaker_id=info[0].speaker_id,
            speaker_portrait=info[0].portrait,
            styles=[
                Style(
                    style_name=i.style_name,
                    style_id=i.style_id,
                    htsvoice=i.htsvoice,
                    portrait=i.portrait,
                    samples=i.samples,
                )
                for i in info
            ],
        )
        styles[speaker_id] = s


def generate_config(info: HtsvoiceFileInfo):
    pass

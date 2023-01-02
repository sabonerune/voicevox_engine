from logging import getLogger
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pyopenjtalk
from pyopenjtalk import tts
from scipy.signal import resample

from voicevox_engine.full_context_label import Phoneme

from ...model import AccentPhrase, AudioQuery
from ...synthesis_engine import SynthesisEngineBase


def accent_phrase_to_phonemes(accent_phrases: List[AccentPhrase]):
    breath_groups: List[List[AccentPhrase]] = []
    breath_group = []
    for accent_phrase in accent_phrases:
        if accent_phrase.pause_mora:
            breath_group.append(accent_phrase)
            breath_groups.append(breath_group)
            breath_group = []
            continue
        breath_group.append(accent_phrase)
    if breath_group:
        breath_groups.append(breath_group)
    _accent_phrases = [
        (accent_phrase, i)
        for i, breath_group in enumerate(breath_groups)
        for accent_phrase in breath_group
    ]
    moras = [
        (mora, i)
        for i, accent_phrase_t in enumerate(_accent_phrases)
        for mora in accent_phrase_t[0].moras
    ]
    phonemes: List[Tuple[str, int]] = []
    for i, mora_t in enumerate(moras):
        mora = mora_t[0]
        if mora.consonant is not None:
            phonemes.append((mora.consonant, i))
        phonemes.append((mora.vowel, i))
    constant_contexts = {
        "b1": "xx",
        "b2": "xx",
        "b3": "xx",
        "c1": "xx",
        "c2": "xx",
        "c3": "xx",
        "d1": "xx",
        "d2": "xx",
        "d3": "xx",
        "e4": "xx",
        "f4": "xx",
        "g4": "xx",
    }
    utterance_contexts = {
        "k1": f"{max(len(breath_groups),19)}",
        "k2": f"{max(len(_accent_phrases),19)}",
        "k3": f"{max(len(moras),19)}",
    }
    last_label_index = len(phonemes)
    label: List[Phoneme] = []
    for i in range(-1, last_label_index):
        contexts = dict(constant_contexts, **utterance_contexts)
        phoneme_object = Phoneme(contexts)
        if i == -1 or i == last_label_index:
            contexts.update(
                {
                    "p3": "sil",
                    "a1": "xx",
                    "a2": "xx",
                    "a3": "xx",
                    "f1": "xx",
                    "f2": "xx",
                    "f3": "xx",
                    "f5": "xx",
                    "f6": "xx",
                    "f7": "xx",
                    "f8": "xx",
                    "i1": "xx",
                    "i2": "xx",
                    "i3": "xx",
                    "i4": "xx",
                    "i5": "xx",
                    "i6": "xx",
                    "i7": "xx",
                    "i8": "xx",
                }
            )
        else:
            current_mora_index = phonemes[i][1]
            current_accent_phrase_index = moras[current_mora_index][1]
            current_breath_group_index = _accent_phrases[current_accent_phrase_index][1]
            accentphrase_indexs_in_current_breath_group = [
                i
                for i, ap in enumerate(_accent_phrases)
                if ap[1] == current_breath_group_index
            ]
            accentphrase_indexs_in_start_to_prev_breath_group = [
                api
                for i in range(0, current_breath_group_index)
                for api, ap in enumerate(_accent_phrases)
                if ap[1] == i
            ]
            accentphrase_indexs_in_next_to_end_breath_group = [
                api
                for i in range(current_breath_group_index, len(breath_groups))
                for api, ap in enumerate(_accent_phrases)
                if ap[1] == i
            ]
            contexts.update(
                {
                    "p3": f"{phonemes[i][0]}",
                    "a1": "xx",
                    "a2": "xx",
                    "a3": "xx",
                    "f1": f"{min(len(_accent_phrases[current_accent_phrase_index][0].moras), 49)}",
                    "f2": f"{min(_accent_phrases[current_accent_phrase_index][0].accent, 49)}",
                    "f3": f"{0 if _accent_phrases[current_accent_phrase_index][0].is_interrogative else 1}",
                    "f5": f"{min(accentphrase_indexs_in_current_breath_group.index(current_accent_phrase_index) + 1, 49)}",
                    "f6": f"{min(0, 49)}",
                    "f7": f"{min(0, 99)}",
                    "f8": f"{min(0, 99)}",
                    "i1": f"{min(len(accentphrase_indexs_in_current_breath_group), 49)}",
                    "i2": f"{min(len([mora for mora in moras if mora[1] in accentphrase_indexs_in_current_breath_group]), 99)}",
                    "i3": f"{min(current_breath_group_index + 1, 19)}",
                    "i4": f"{min(len(breath_groups) - current_breath_group_index, 19)}",
                    "i5": f"{min(len([i for bg in breath_groups[:current_breath_group_index] for i in bg]) + 1, 49)}",
                    "i6": f"{min(len([i for bg in breath_groups[current_breath_group_index:] for i in bg]), 49)}",
                    "i7": f"{min(len([mora for mora in moras if mora[1] in accentphrase_indexs_in_start_to_prev_breath_group]) + 1, 199)}",
                    "i8": f"{min(len([mora for mora in moras if mora[1] in accentphrase_indexs_in_next_to_end_breath_group]) + 1, 199)}",
                }
            )
            i
        i


def create_phoneme_list(accent_phrases: List[AccentPhrase]):
    class Context:
        def __init__(self) -> None:
            self.breath_groups: list["Bg"] = []
            self.accent_phrases: list["Ap"] = []
            self.moras: list["Mo"] = []
            self.labels: list["ContextLabel"] = []

        def append_bg(self, bg: "Bg"):
            self.breath_groups.append(bg)

        def append_ap(self, ap: "Ap"):
            self.accent_phrases.append(ap)

        def append_mo(self, mo: "Mo"):
            self.moras.append(mo)

        def append_label(self, label: "ContextLabel"):
            self.labels.append(label)

    class Bg:
        def __init__(self, context: Context) -> None:
            context.append_bg(self)
            self._context = context

        def breath_group(self, shift: int):
            bg = self._context.breath_groups
            index = bg.index(self) + shift
            if index < 0 or len(bg) <= index:
                return None
            return bg[index]

        def accent_phrases(self):
            return [i for i in self._context.accent_phrases if i._bg is self]

        def accent_len(self):
            return len(self.accent_phrases())

        def moras(self):
            return [i for i in self._context.moras if i._ap._bg is self]

        def mora_len(self):
            return len(self.moras())

        def pos_backword_by_bg(self):
            return self._context.breath_groups.index(self) + 1

        def pos_forword_by_bg(self):
            bg_list = self._context.breath_groups
            index = bg_list.index(self)
            return len(bg_list) - index

        def pos_backword_by_ap(self):
            bg_list = self._context.breath_groups
            index = bg_list.index(self)
            return sum([i.accent_len() for i in bg_list[0:index]]) + 1

        def pos_forword_by_ap(self):
            bg_list = self._context.breath_groups
            index = bg_list.index(self)
            return sum([i.accent_len() for i in bg_list[index:]])

        def pos_backword_by_mo(self):
            bg_list = self._context.breath_groups
            index = bg_list.index(self)
            return sum([i.mora_len() for i in bg_list[0:index]]) + 1

        def pos_forword_by_mo(self):
            bg_list = self._context.breath_groups
            index = bg_list.index(self)
            return sum([i.mora_len() for i in bg_list[index:]])

    class Ap:
        def __init__(
            self,
            context: Context,
            bg: Bg,
            accent: Optional[int] = None,
            is_interrogative: Optional[bool] = False,
            has_pau: Optional[bool] = False,
        ) -> None:
            context.append_ap(self)
            self._context = context
            self._bg = bg
            self._accent = accent
            self.is_interrogative = is_interrogative
            self._has_pau = has_pau

        def accent_phrase(self, shift: int):
            ap = self._context.accent_phrases
            index = ap.index(self) + shift
            if index < 0 or len(ap) <= index:
                return None
            return ap[index]

        def moras(self):
            return [i for i in self._context.moras if i._ap is self]

        def mora_len(self):
            m_len = len(self.moras())
            return m_len if m_len != 0 else "xx"

        def accent(self):
            return self._accent

        def interrogative(self):
            if self.is_interrogative is None:
                return None
            return 1 if self.is_interrogative else 0

        def has_pau(self):
            if self._has_pau is None:
                return None
            return 0 if self._has_pau else 1

        def pos_backword_by_ap(self):
            return self._bg.accent_phrases().index(self) + 1

        def pos_forward_by_ap(self):
            ap_list = self._bg.accent_phrases()
            index = ap_list.index(self)
            return len(ap_list) - index

        def pos_backword_by_mora(self):
            ap_list = self._bg.accent_phrases()
            index = ap_list.index(self)
            aps = ap_list[0:index]
            return sum([i.mora_len() for i in aps]) + 1

        def pos_forward_by_mora(self):
            ap_list = self._bg.accent_phrases()
            index = ap_list.index(self)
            aps = ap_list[index:]
            return sum([i.mora_len() for i in aps])

    class Mo:
        def __init__(self, context: Context, ap: Ap) -> None:
            context.append_mo(self)
            self._context = context
            self._ap = ap

        def diff_accent(self):
            moras = self._ap.moras()
            index = moras.index(self) + 1
            return index - self._ap._accent

        def pos_backword(self):
            moras = self._ap.moras()
            return moras.index(self) + 1

        def pos_forward(self):
            moras = self._ap.moras()
            index = moras.index(self)
            return len(moras) - index

    class ContextLabel:
        def __init__(
            self, context: Context, ap: Optional[Ap], mo: Optional[Mo], phoneme: str
        ) -> None:
            context.append_label(self)
            self._context = context
            self._ap = ap
            self._mo = mo
            self._phoneme = phoneme

        def phoneme_identity(self, shift: int):
            if shift == 0:
                return self._phoneme
            labels = self._context.labels
            index = labels.index(self) + shift
            if index < 0 or len(labels) <= index:
                return "xx"
            return labels[index]._phoneme

        def p1(self):
            return str(self.phoneme_identity(-2))

        def p2(self):
            return str(self.phoneme_identity(-1))

        def p3(self):
            return str(self.phoneme_identity(0))

        def p4(self):
            return str(self.phoneme_identity(1))

        def p5(self):
            return str(self.phoneme_identity(2))

        def a1(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._mo.diff_accent())

        def a2(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._mo.pos_backword())

        def a3(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._mo.pos_forward())

        def b1(self):
            return "xx"

        def b2(self):
            return "xx"

        def b3(self):
            return "xx"

        def c1(self):
            return "xx"

        def c2(self):
            return "xx"

        def c3(self):
            return "xx"

        def d1(self):
            return "xx"

        def d2(self):
            return "xx"

        def d3(self):
            return "xx"

        def e1(self):
            shift = -1 if self._phoneme != "pau" else 0
            f_ap = self._ap.accent_phrase(shift)
            if f_ap is None:
                return "xx"
            return str(f_ap.mora_len())

        def e2(self):
            shift = -1 if self._phoneme != "pau" else 0
            f_ap = self._ap.accent_phrase(shift)
            if f_ap is None:
                return "xx"
            ac = f_ap.accent()
            return str(ac) if ac is not None else "xx"

        def e3(self):
            shift = -1 if self._phoneme != "pau" else 0
            f_ap = self._ap.accent_phrase(shift)
            if f_ap is None:
                return "xx"
            ac = f_ap.interrogative()
            return str(ac) if ac is not None else "xx"

        def e4(self):
            return "xx"

        def e5(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            f_ap = self._ap.accent_phrase(-1)
            if f_ap is None:
                return "xx"
            pau = f_ap.has_pau()
            return str(pau) if pau is not None else "xx"

        def f1(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.mora_len())

        def f2(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.accent())

        def f3(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.interrogative())

        def f4(self):
            return "xx"

        def f5(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.pos_backword_by_ap())

        def f6(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.pos_forward_by_ap())

        def f7(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.pos_backword_by_mora())

        def f8(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap.pos_forward_by_mora())

        def g1(self):
            f_ap = self._ap.accent_phrase(1)
            if f_ap is None:
                return "xx"
            return str(f_ap.mora_len())

        def g2(self):
            f_ap = self._ap.accent_phrase(1)
            if f_ap is None:
                return "xx"
            ac = f_ap.accent()
            return str(ac) if ac is not None else "xx"

        def g3(self):
            f_ap = self._ap.accent_phrase(1)
            if f_ap is None:
                return "xx"
            ac = f_ap.interrogative()
            return str(ac) if ac is not None else "xx"

        def g4(self):
            return "xx"

        def g5(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            if (
                self._ap is None
                or len(self._context.accent_phrases)
                <= self._context.accent_phrases.index(self._ap) + 2
            ):
                return "xx"
            pau = self._ap.has_pau()
            return str(pau) if pau is not None else "xx"

        def h1(self):
            labels = self._context.labels
            last_index = len(labels) - 1
            if last_index == labels.index(self):
                return str(self._context.breath_groups[-1].accent_len())
            if self._ap is None or self._ap._bg is None:
                return "xx"
            shift = -1 if self._phoneme != "pau" else 0
            back_bg = self._ap._bg.breath_group(shift)
            if back_bg is None:
                return "xx"
            return str(back_bg.accent_len())

        def h2(self):
            labels = self._context.labels
            last_index = len(labels) - 1
            if last_index == labels.index(self):
                return str(self._context.breath_groups[-1].mora_len())
            if self._ap is None or self._ap._bg is None:
                return "xx"
            shift = -1 if self._phoneme != "pau" else 0
            back_bg = self._ap._bg.breath_group(shift)
            if back_bg is None:
                return "xx"
            return str(back_bg.mora_len())

        def i1(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.accent_len())

        def i2(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.mora_len())

        def i3(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.pos_backword_by_bg())

        def i4(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.pos_forword_by_bg())

        def i5(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.pos_backword_by_ap())

        def i6(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.pos_forword_by_ap())

        def i7(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.pos_backword_by_mo())

        def i8(self):
            if self._phoneme == "sil" or self._phoneme == "pau":
                return "xx"
            return str(self._ap._bg.pos_forword_by_mo())

        def j1(self):
            if self._context.labels.index(self) == 0:
                return str(self._context.labels[1]._ap._bg.accent_len())
            if self._ap is None or self._ap._bg is None:
                return "xx"
            back_bg = self._ap._bg.breath_group(1)
            if back_bg is None:
                return "xx"
            return str(back_bg.accent_len())

        def j2(self):
            if self._context.labels.index(self) == 0:
                return str(self._context.labels[1]._ap._bg.mora_len())
            if self._ap is None or self._ap._bg is None:
                return "xx"
            back_bg = self._ap._bg.breath_group(1)
            if back_bg is None:
                return "xx"
            return str(back_bg.mora_len())

        def k1(self):
            return str(len(self._context.breath_groups))

        def k2(self):
            aps = [i for i in self._context.accent_phrases if i._bg]
            return str(len(aps))

        def k3(self):
            return str(len(self._context.moras))

        def label(self) -> Phoneme:
            context = {
                "p1": self.p1(),
                "p2": self.p2(),
                "p3": self.p3(),
                "p4": self.p4(),
                "p5": self.p5(),
                "a1": self.a1(),
                "a2": self.a2(),
                "a3": self.a3(),
                "b1": "xx",
                "b2": "xx",
                "b3": "xx",
                "c1": "xx",
                "c2": "xx",
                "c3": "xx",
                "d1": "xx",
                "d2": "xx",
                "d3": "xx",
                "e1": self.e1(),
                "e2": self.e2(),
                "e3": self.e3(),
                "e4": self.e4(),
                "e5": self.e5(),
                "f1": self.f1(),
                "f2": self.f2(),
                "f3": self.f3(),
                "f4": self.f4(),
                "f5": self.f5(),
                "f6": self.f6(),
                "f7": self.f7(),
                "f8": self.f8(),
                "g1": self.g1(),
                "g2": self.g2(),
                "g3": self.g3(),
                "g4": self.g4(),
                "g5": self.g5(),
                "h1": self.h1(),
                "h2": self.h2(),
                "i1": self.i1(),
                "i2": self.i2(),
                "i3": self.i3(),
                "i4": self.i4(),
                "i5": self.i5(),
                "i6": self.i6(),
                "i7": self.i7(),
                "i8": self.i8(),
                "j1": self.j1(),
                "j2": self.j2(),
                "k1": self.k1(),
                "k2": self.k2(),
                "k3": self.k3(),
            }
            return Phoneme(context)

    context = Context()
    s_sil_ap = Ap(context, None, None, None, None)
    ContextLabel(context, s_sil_ap, None, "sil")
    sprit_index: list[int] = [0]
    for ii, i in enumerate(accent_phrases):
        if i.pause_mora:
            sprit_index.append(ii + 1)
    sprit_index.append(len(accent_phrases))
    for ii, i in enumerate(sprit_index[1:]):
        b_group = accent_phrases[sprit_index[ii] : i]
        bg = Bg(context)
        for accent_phrase in b_group:
            ap = Ap(
                context,
                bg,
                accent_phrase.accent,
                accent_phrase.is_interrogative,
                bool(accent_phrase.pause_mora),
            )
            for mora in accent_phrase.moras:
                mo = Mo(context, ap)
                if mora.consonant:
                    ContextLabel(context, ap, mo, mora.consonant)
                ContextLabel(context, ap, mo, mora.vowel)
            if accent_phrase.pause_mora:
                ContextLabel(context, ap, None, accent_phrase.pause_mora.vowel)
    e_sil_ap = Ap(context, None, None, None, None)
    ContextLabel(context, e_sil_ap, None, "sil")
    return context.labels


class MockSynthesisEngine(SynthesisEngineBase):
    """
    SynthesisEngine [Mock]
    """

    def __init__(
        self,
        speakers: str,
        supported_devices: Optional[str] = None,
    ):
        """
        __init__ [Mock]
        """
        super().__init__()

        self._speakers = speakers
        self._supported_devices = supported_devices
        self.default_sampling_rate = 24000

    @property
    def speakers(self) -> str:
        return self._speakers

    @property
    def supported_devices(self) -> Optional[str]:
        return self._supported_devices

    def replace_phoneme_length(
        self, accent_phrases: List[AccentPhrase], speaker_id: int
    ) -> List[AccentPhrase]:
        """
        replace_phoneme_length 入力accent_phrasesを変更せずにそのまま返します [Mock]

        Parameters
        ----------
        accent_phrases : List[AccentPhrase]
            フレーズ句のリスト
        speaker_id : int
            話者

        Returns
        -------
        List[AccentPhrase]
            フレーズ句のリスト（変更なし）
        """
        return accent_phrases

    def replace_mora_pitch(
        self, accent_phrases: List[AccentPhrase], speaker_id: int
    ) -> List[AccentPhrase]:
        """
        replace_mora_pitch 入力accent_phrasesを変更せずにそのまま返します [Mock]

        Parameters
        ----------
        accent_phrases : List[AccentPhrase]
            フレーズ句のリスト
        speaker_id : int
            話者

        Returns
        -------
        List[AccentPhrase]
            フレーズ句のリスト（変更なし）
        """
        return accent_phrases

    def _synthesis_impl(self, query: AudioQuery, speaker_id: int) -> np.ndarray:
        """
        synthesis voicevox coreを使わずに、音声合成する [Mock]

        Parameters
        ----------
        query : AudioQuery
            /audio_query APIで得たjson
        speaker_id : int
            話者

        Returns
        -------
        wave [npt.NDArray[np.int16]]
            音声波形データをNumPy配列で返します
        """
        # recall text in katakana
        # flatten_moras = to_flatten_moras(query.accent_phrases)
        # kana_text = "".join([mora.text for mora in flatten_moras])

        # wave = self.forward(kana_text)
        wave, sr = pyopenjtalk.synthesize(
            [i.label().label for i in create_phoneme_list(query.accent_phrases)]
        )
        if query.outputSamplingRate != sr:
            wave = resample(wave, query.outputSamplingRate * len(wave) // sr)

        # volume
        wave *= query.volumeScale

        return wave.astype("int16")

    def forward(self, text: str, **kwargs: Dict[str, Any]) -> np.ndarray:
        """
        forward tts via pyopenjtalk.tts()
        参照→SynthesisEngine のdocstring [Mock]

        Parameters
        ----------
        text : str
            入力文字列（例：読み上げたい文章をカタカナにした文字列、等）

        Returns
        -------
        wave [npt.NDArray[np.int16]]
            音声波形データをNumPy配列で返します

        Note
        -------
        ここで行う音声合成では、調声（ピッチ等）を反映しない

        # pyopenjtalk.tts()の出力仕様
        dtype=np.float64, 16 bit, mono 48000 Hz

        # resampleの説明
        非モック実装（decode_forward）と合わせるために、出力を24kHzに変換した。
        """
        logger = getLogger("uvicorn")  # FastAPI / Uvicorn 内からの利用のため
        logger.info("[Mock] input text: %s" % text)
        wave, sr = tts(text)
        wave = resample(wave, 24000 * len(wave) // 48000)
        return wave

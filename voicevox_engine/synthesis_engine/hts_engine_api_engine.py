from typing import List, Optional, Tuple

import numpy as np
from pyopenjtalk import synthesize
from scipy.signal import resample

from voicevox_engine.full_context_label import Phoneme
from voicevox_engine.model import AccentPhrase, AudioQuery
from .synthesis_engine import SynthesisEngineBase


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
        current_accent_phrase = _accent_phrases[mora_t[1]][0]
        if current_accent_phrase.pause_mora and current_accent_phrase.moras[-1] == mora:
            phonemes.append((current_accent_phrase.pause_mora.vowel, i))
    contexts_ap = []
    for ap_index, (accent_phrase, current_bg_index) in enumerate(_accent_phrases):
        ap_indexs_in_current_breath_group = [
            i
            for i, accent_phrase in enumerate(_accent_phrases)
            if accent_phrase[1] == current_bg_index
        ]
        current_ap_index_in_currentbreath_group = (
            ap_indexs_in_current_breath_group.index(ap_index)
        )
        ap_indexs_in_current_breath_group_by_mora = [
            i for _, i in moras if _accent_phrases[i][1] == current_bg_index
        ]
        current_ap_indexs_in_current_breath_group_by_mora = (
            ap_indexs_in_current_breath_group_by_mora.index(ap_index)
        )
        prev_accent_phrase_index = index if (index := ap_index - 1) >= 0 else None
        if prev_accent_phrase_index is not None:
            prev_mora_len = min(
                len(_accent_phrases[prev_accent_phrase_index][0].moras), 49
            )
            prev_accent = min(_accent_phrases[prev_accent_phrase_index][0].accent, 49)
            prev_interrogative = (
                1
                if _accent_phrases[prev_accent_phrase_index][0].is_interrogative
                else 0
            )
            prev_pause = (
                0
                if _accent_phrases[prev_accent_phrase_index][0].pause_mora is not None
                else 1
            )
        next_accent_phrase_index = (
            index if (index := ap_index + 1) < len(_accent_phrases) else None
        )
        if next_accent_phrase_index is not None:
            next_mora_len = min(
                len(_accent_phrases[next_accent_phrase_index][0].moras), 49
            )
            next_accent = min(_accent_phrases[next_accent_phrase_index][0].accent, 49)
            next_interrogative = (
                1
                if _accent_phrases[next_accent_phrase_index][0].is_interrogative
                else 0
            )
            next_pause = 0 if accent_phrase.pause_mora is not None else 1
        contexts_ap.append(
            {
                "e1": "xx" if prev_accent_phrase_index is None else str(prev_mora_len),
                "e2": "xx" if prev_accent_phrase_index is None else str(prev_accent),
                "e3": "xx"
                if prev_accent_phrase_index is None
                else str(prev_interrogative),
                "e5": "xx" if prev_accent_phrase_index is None else str(prev_pause),
                "f1": str(min(len(accent_phrase.moras), 49)),
                "f2": str(min(accent_phrase.accent, 49)),
                "f3": str(1 if accent_phrase.is_interrogative else 0),
                "f5": str(min(current_ap_index_in_currentbreath_group + 1, 49)),
                "f6": str(
                    min(
                        len(ap_indexs_in_current_breath_group)
                        - current_ap_index_in_currentbreath_group,
                        49,
                    )
                ),
                "f7": str(
                    min(current_ap_indexs_in_current_breath_group_by_mora + 1, 99)
                ),
                "f8": str(
                    min(
                        len(ap_indexs_in_current_breath_group_by_mora)
                        - current_ap_indexs_in_current_breath_group_by_mora,
                        99,
                    )
                ),
                "g1": "xx" if next_accent_phrase_index is None else str(next_mora_len),
                "g2": "xx" if next_accent_phrase_index is None else str(next_accent),
                "g3": "xx"
                if next_accent_phrase_index is None
                else str(next_interrogative),
                "g5": "xx" if next_accent_phrase_index is None else str(next_pause),
            }
        )
    contexts_bg = []
    for current_breath_group_index, _ in enumerate(breath_groups):
        ap_indexs_in_current_breath_group = [
            i
            for i, (_, breath_group_index) in enumerate(_accent_phrases)
            if breath_group_index == current_breath_group_index
        ]
        accentphrase_indexs_in_start_to_prev_breath_group = [
            ap_index
            for i in range(0, current_breath_group_index)
            for ap_index, (_, bg_index) in enumerate(_accent_phrases)
            if bg_index == i
        ]
        accentphrase_indexs_in_next_to_end_breath_group = [
            ap_index
            for i in range(current_breath_group_index, len(breath_groups))
            for ap_index, (_, bg_index) in enumerate(_accent_phrases)
            if bg_index == i
        ]
        prev_breath_group_index = (
            index if (index := current_breath_group_index - 1) >= 0 else None
        )
        if prev_breath_group_index is not None:
            prev_ap_len = len(breath_groups[prev_breath_group_index])
            ap_indexs_in_prev_breath_group = [
                i
                for i, (_, breath_group_index) in enumerate(_accent_phrases)
                if breath_group_index == prev_breath_group_index
            ]
            prev_mora_len = sum(
                accent_phrase_index in ap_indexs_in_prev_breath_group
                for _, accent_phrase_index in moras
            )
        next_breath_group_index = (
            index
            if len(breath_groups) > (index := current_breath_group_index + 1)
            else None
        )
        if next_breath_group_index is not None:
            next_ap_len = len(breath_groups[next_breath_group_index])
            ap_indexs_in_next_breath_group = [
                i
                for i, (_, breath_group_index) in enumerate(_accent_phrases)
                if breath_group_index == next_breath_group_index
            ]
            next_mora_len = sum(
                accent_phrase_index in ap_indexs_in_next_breath_group
                for _, accent_phrase_index in moras
            )
        contexts_bg.append(
            {
                "h1": "xx"
                if prev_breath_group_index is None
                else str(min(prev_ap_len, 49)),
                "h2": "xx"
                if prev_breath_group_index is None
                else str(min(prev_mora_len, 99)),
                "i1": str(min(len(ap_indexs_in_current_breath_group), 49)),
                "i2": str(
                    min(
                        sum(
                            accent_phrase_index in ap_indexs_in_current_breath_group
                            for _, accent_phrase_index in moras
                        ),
                        99,
                    )
                ),
                "i3": str(min(current_breath_group_index + 1, 19)),
                "i4": str(min(len(breath_groups) - current_breath_group_index, 19)),
                "i5": str(
                    min(
                        len(
                            [
                                i
                                for bg in breath_groups[:current_breath_group_index]
                                for i in bg
                            ]
                        )
                        + 1,
                        49,
                    )
                ),
                "i6": str(
                    min(
                        len(
                            [
                                i
                                for bg in breath_groups[current_breath_group_index:]
                                for i in bg
                            ]
                        ),
                        49,
                    )
                ),
                "i7": str(
                    min(
                        sum(
                            ap_index
                            in accentphrase_indexs_in_start_to_prev_breath_group
                            for _, ap_index in moras
                        )
                        + 1,
                        199,
                    )
                ),
                "i8": str(
                    min(
                        sum(
                            ap_index in accentphrase_indexs_in_next_to_end_breath_group
                            for _, ap_index in moras
                        ),
                        199,
                    )
                ),
                "j1": "xx"
                if next_breath_group_index is None
                else str(min(next_ap_len, 49)),
                "j2": "xx"
                if next_breath_group_index is None
                else str(min(next_mora_len, 99)),
            }
        )
    constant_contexts = {
        "p1": "xx",
        "p2": "xx",
        "p4": "xx",
        "p5": "xx",
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
        "k1": str(min(len(breath_groups), 19)),
        "k2": str(min(len(_accent_phrases), 49)),
        "k3": str(min(len(moras), 199)),
    }
    last_label_index = len(phonemes)
    label: List[Phoneme] = []
    for i in range(-1, last_label_index + 1):
        contexts = dict(constant_contexts, **utterance_contexts)
        phoneme_object = Phoneme(contexts)
        if i == -1 or i == last_label_index or phonemes[i][0] == "pau":
            if i == -1:
                p3 = "sil"
                e1 = "xx"
                e2 = "xx"
                e3 = "xx"
                next_ap_index = moras[phonemes[0][1]][1]
                g1 = contexts_ap[next_ap_index]["f1"]
                g2 = contexts_ap[next_ap_index]["f2"]
                g3 = contexts_ap[next_ap_index]["f3"]
                h1 = "xx"
                h2 = "xx"
                next_bg_index = _accent_phrases[0][1]
                j1 = contexts_bg[next_bg_index]["i1"]
                j2 = contexts_bg[next_bg_index]["i2"]
            elif i == last_label_index:
                p3 = "sil"
                prev_ap_index = moras[phonemes[-1][1]][1]
                e1 = contexts_ap[prev_ap_index]["f1"]
                e2 = contexts_ap[prev_ap_index]["f2"]
                e3 = contexts_ap[prev_ap_index]["f3"]
                g1 = "xx"
                g2 = "xx"
                g3 = "xx"
                prev_bg_index = _accent_phrases[-1][1]
                h1 = contexts_bg[prev_bg_index]["i1"]
                h2 = contexts_bg[prev_bg_index]["i2"]
                j1 = "xx"
                j2 = "xx"
            else:
                p3 = "pau"
                prev_ap_index = moras[phonemes[i][1]][1]
                e1 = contexts_ap[prev_ap_index]["f1"]
                e2 = contexts_ap[prev_ap_index]["f2"]
                e3 = contexts_ap[prev_ap_index]["f3"]
                g1 = contexts_ap[prev_ap_index + 1]["f1"]
                g2 = contexts_ap[prev_ap_index + 1]["f2"]
                g3 = contexts_ap[prev_ap_index + 1]["f3"]
                prev_bg_index = _accent_phrases[moras[phonemes[i][1]][1]][1]
                h1 = contexts_bg[prev_bg_index]["i1"]
                h2 = contexts_bg[prev_bg_index]["i2"]
                j1 = contexts_bg[prev_bg_index + 1]["i1"]
                j2 = contexts_bg[prev_bg_index + 1]["i2"]
            contexts.update(
                {
                    "p3": p3,
                    "a1": "xx",
                    "a2": "xx",
                    "a3": "xx",
                    "e1": f"{e1}",
                    "e2": f"{e2}",
                    "e3": f"{e3}",
                    "e5": "xx",
                    "f1": "xx",
                    "f2": "xx",
                    "f3": "xx",
                    "f5": "xx",
                    "f6": "xx",
                    "f7": "xx",
                    "f8": "xx",
                    "g1": f"{g1}",
                    "g2": f"{g2}",
                    "g3": f"{g3}",
                    "g5": "xx",
                    "h1": f"{h1}",
                    "h2": f"{h2}",
                    "i1": "xx",
                    "i2": "xx",
                    "i3": "xx",
                    "i4": "xx",
                    "i5": "xx",
                    "i6": "xx",
                    "i7": "xx",
                    "i8": "xx",
                    "j1": f"{j1}",
                    "j2": f"{j2}",
                }
            )
        else:
            current_mora_index = phonemes[i][1]
            current_accent_phrase_index = moras[current_mora_index][1]
            current_breath_group_index = _accent_phrases[current_accent_phrase_index][1]
            accent = _accent_phrases[current_accent_phrase_index][0].accent
            mora_indexs_in_current_accent_phrase = [
                i
                for i, mora in enumerate(moras)
                if mora[1] == current_accent_phrase_index
            ]
            difference_between_accent_position_current_mora = (
                mora_indexs_in_current_accent_phrase.index(current_mora_index)
                - accent
                + 1
            )
            contexts.update(
                {
                    "p3": str(phonemes[i][0]),
                    "a1": str(
                        max(
                            min(difference_between_accent_position_current_mora, 49),
                            -49,
                        )
                    ),
                    "a2": str(
                        min(
                            mora_indexs_in_current_accent_phrase.index(
                                current_mora_index
                            )
                            + 1,
                            49,
                        )
                    ),
                    "a3": str(
                        min(
                            len(mora_indexs_in_current_accent_phrase)
                            - mora_indexs_in_current_accent_phrase.index(
                                current_mora_index
                            ),
                            49,
                        )
                    ),
                    **contexts_ap[current_accent_phrase_index],
                    **contexts_bg[current_breath_group_index],
                }
            )
        label.append(phoneme_object)
    for i, phoneme in enumerate(label):
        contexts = phoneme.contexts
        previous_index = i - 1
        if 0 <= previous_index:
            previous_contexts = label[previous_index].contexts
            contexts["p2"] = previous_contexts["p3"]
            before_previous_index = i - 2
            if 0 <= before_previous_index:
                contexts["p1"] = label[before_previous_index].contexts["p3"]
        next_index = i + 1
        if next_index < len(label):
            next_contexts = label[next_index].contexts
            contexts["p4"] = next_contexts["p3"]
            after_next_index = i + 2
            if after_next_index < len(label):
                contexts["p5"] = label[after_next_index].contexts["p3"]
    return label


class HtsEngineApiEngine(SynthesisEngineBase):
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

        phonemes = accent_phrase_to_phonemes(query.accent_phrases)
        wave, sr = synthesize([i.label for i in phonemes], query.speedScale)

        # volume
        wave *= query.volumeScale
        if sr != query.outputSamplingRate:
            wave = resample(wave, query.outputSamplingRate * len(wave) // sr)

        return wave.astype("int16")

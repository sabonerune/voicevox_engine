from typing import List
from unittest import TestCase

import pyopenjtalk

from voicevox_engine.dev.synthesis_engine import mock
from voicevox_engine.full_context_label import Phoneme
from voicevox_engine.model import AccentPhrase, Mora
from voicevox_engine.synthesis_engine import synthesis_engine_base


class Test_gen(TestCase):
    def test_fcl(self):
        test_text = "彼女はその事件を、生き生きとした筆致で描写した。"
        utterance = synthesis_engine_base.extract_full_context_label(test_text)
        accent_phrases = [
            AccentPhrase(
                moras=synthesis_engine_base.full_context_label_moras_to_moras(
                    accent_phrase.moras
                ),
                accent=accent_phrase.accent,
                pause_mora=(
                    Mora(
                        text="、",
                        consonant=None,
                        consonant_length=None,
                        vowel="pau",
                        vowel_length=0,
                        pitch=0,
                    )
                    if (
                        i_accent_phrase == len(breath_group.accent_phrases) - 1
                        and i_breath_group != len(utterance.breath_groups) - 1
                    )
                    else None
                ),
                is_interrogative=accent_phrase.is_interrogative,
            )
            for i_breath_group, breath_group in enumerate(utterance.breath_groups)
            for i_accent_phrase, accent_phrase in enumerate(breath_group.accent_phrases)
        ]
        regen = mock.accent_phrase_to_phonemes(accent_phrases)
        base_label = [
            Phoneme.from_label(i) for i in pyopenjtalk.extract_fullcontext(test_text)
        ]
        for (i, _) in enumerate(base_label):
            self.assertEqual(regen[i].contexts["p3"], base_label[i].contexts["p3"])
            self.assertEqual(regen[i].contexts["a1"], base_label[i].contexts["a1"])
            self.assertEqual(regen[i].contexts["a2"], base_label[i].contexts["a2"])
            self.assertEqual(regen[i].contexts["a3"], base_label[i].contexts["a3"])
            self.assertEqual(regen[i].contexts["f1"], base_label[i].contexts["f1"])
            self.assertEqual(regen[i].contexts["f2"], base_label[i].contexts["f2"])
            self.assertEqual(regen[i].contexts["f3"], base_label[i].contexts["f3"])
            self.assertEqual(regen[i].contexts["f4"], base_label[i].contexts["f4"])
            self.assertEqual(regen[i].contexts["f5"], base_label[i].contexts["f5"])
            self.assertEqual(regen[i].contexts["f6"], base_label[i].contexts["f6"])
            self.assertEqual(regen[i].contexts["f7"], base_label[i].contexts["f7"])
            self.assertEqual(regen[i].contexts["f8"], base_label[i].contexts["f8"])
            self.assertEqual(regen[i].contexts["i1"], base_label[i].contexts["i1"])
            self.assertEqual(regen[i].contexts["i2"], base_label[i].contexts["i2"])
            self.assertEqual(regen[i].contexts["i3"], base_label[i].contexts["i3"])
            self.assertEqual(regen[i].contexts["i4"], base_label[i].contexts["i4"])
            self.assertEqual(regen[i].contexts["i5"], base_label[i].contexts["i5"])
            self.assertEqual(regen[i].contexts["i6"], base_label[i].contexts["i6"])
            self.assertEqual(regen[i].contexts["i7"], base_label[i].contexts["i7"])
            self.assertEqual(regen[i].contexts["i8"], base_label[i].contexts["i8"])
            self.assertEqual(regen[i].contexts["k1"], base_label[i].contexts["k1"])
            self.assertEqual(regen[i].contexts["k2"], base_label[i].contexts["k2"])
            self.assertEqual(regen[i].contexts["k3"], base_label[i].contexts["k3"])

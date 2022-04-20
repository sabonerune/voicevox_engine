import unittest
from unittest import TestCase

import pyopenjtalk

from voicevox_engine.dev.core import metas as mock_metas
from voicevox_engine.dev.core import supported_devices as mock_supported_devices
from voicevox_engine.dev.synthesis_engine.mock import (
    MockSynthesisEngine,
    create_phoneme_list,
)
from voicevox_engine.full_context_label import Phoneme


class TestAccent2contextLabel(TestCase):

    mock_engine = MockSynthesisEngine(
        speakers=mock_metas(), supported_devices=mock_supported_devices()
    )
    text = "おはようございます。元気ですか？私は元気です！"
    full_context_label = pyopenjtalk.extract_fullcontext(text)
    phoneme = [Phoneme.from_label(i) for i in full_context_label]
    accent_phrase = mock_engine.create_accent_phrases(text, 0)
    label = create_phoneme_list(accent_phrase)

    def test_p1(self):
        phoneme = [i.contexts["p1"] for i in self.phoneme]
        label = [i.p1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_p2(self):
        phoneme = [i.contexts["p2"] for i in self.phoneme]
        label = [i.p2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_p3(self):
        phoneme = [i.contexts["p3"] for i in self.phoneme]
        label = [i.p3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_p4(self):
        phoneme = [i.contexts["p4"] for i in self.phoneme]
        label = [i.p4() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_p5(self):
        phoneme = [i.contexts["p5"] for i in self.phoneme]
        label = [i.p5() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_a1(self):
        phoneme = [i.contexts["a1"] for i in self.phoneme]
        label = [i.a1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_a2(self):
        phoneme = [i.contexts["a2"] for i in self.phoneme]
        label = [i.a2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_a3(self):
        phoneme = [i.contexts["a3"] for i in self.phoneme]
        label = [i.a3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_e1(self):
        phoneme = [i.contexts["e1"] for i in self.phoneme]
        label = [i.e1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_e2(self):
        phoneme = [i.contexts["e2"] for i in self.phoneme]
        label = [i.e2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_e3(self):
        phoneme = [i.contexts["e3"] for i in self.phoneme]
        label = [i.e3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_e5(self):
        phoneme = [i.contexts["e5"] for i in self.phoneme]
        label = [i.e5() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f1(self):
        phoneme = [i.contexts["f1"] for i in self.phoneme]
        label = [i.f1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f2(self):
        phoneme = [i.contexts["f2"] for i in self.phoneme]
        label = [i.f2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f3(self):
        phoneme = [i.contexts["f3"] for i in self.phoneme]
        label = [i.f3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f5(self):
        phoneme = [i.contexts["f5"] for i in self.phoneme]
        label = [i.f5() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f6(self):
        phoneme = [i.contexts["f6"] for i in self.phoneme]
        label = [i.f6() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f7(self):
        phoneme = [i.contexts["f7"] for i in self.phoneme]
        label = [i.f7() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_f8(self):
        phoneme = [i.contexts["f8"] for i in self.phoneme]
        label = [i.f8() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_g1(self):
        phoneme = [i.contexts["g1"] for i in self.phoneme]
        label = [i.g1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_g2(self):
        phoneme = [i.contexts["g2"] for i in self.phoneme]
        label = [i.g2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_g3(self):
        phoneme = [i.contexts["g3"] for i in self.phoneme]
        label = [i.g3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_g5(self):
        phoneme = [i.contexts["g5"] for i in self.phoneme]
        label = [i.g5() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_h1(self):
        phoneme = [i.contexts["h1"] for i in self.phoneme]
        label = [i.h1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_h2(self):
        phoneme = [i.contexts["h2"] for i in self.phoneme]
        label = [i.h2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i1(self):
        phoneme = [i.contexts["i1"] for i in self.phoneme]
        label = [i.i1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i2(self):
        phoneme = [i.contexts["i2"] for i in self.phoneme]
        label = [i.i2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i3(self):
        phoneme = [i.contexts["i3"] for i in self.phoneme]
        label = [i.i3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i4(self):
        phoneme = [i.contexts["i4"] for i in self.phoneme]
        label = [i.i4() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i5(self):
        phoneme = [i.contexts["i5"] for i in self.phoneme]
        label = [i.i5() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i6(self):
        phoneme = [i.contexts["i6"] for i in self.phoneme]
        label = [i.i6() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i7(self):
        phoneme = [i.contexts["i7"] for i in self.phoneme]
        label = [i.i7() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_i8(self):
        phoneme = [i.contexts["i8"] for i in self.phoneme]
        label = [i.i8() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_j1(self):
        phoneme = [i.contexts["j1"] for i in self.phoneme]
        label = [i.j1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_j2(self):
        phoneme = [i.contexts["j2"] for i in self.phoneme]
        label = [i.j2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_k1(self):
        phoneme = [i.contexts["k1"] for i in self.phoneme]
        label = [i.k1() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_k2(self):
        phoneme = [i.contexts["k2"] for i in self.phoneme]
        label = [i.k2() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_k3(self):
        phoneme = [i.contexts["k3"] for i in self.phoneme]
        label = [i.k3() for i in self.label]
        self.assertEqual(label, phoneme)

    def test_label(self):
        for i in self.phoneme:
            i.contexts["b1"] = "xx"
            i.contexts["b2"] = "xx"
            i.contexts["b3"] = "xx"
            i.contexts["c1"] = "xx"
            i.contexts["c2"] = "xx"
            i.contexts["c3"] = "xx"
            i.contexts["d1"] = "xx"
            i.contexts["d2"] = "xx"
            i.contexts["d3"] = "xx"
        label = [i.label().label for i in self.label]
        phoneme = [i.label for i in self.phoneme]
        self.assertEqual(label, phoneme)

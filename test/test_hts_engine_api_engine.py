from unittest import TestCase

from pyopenjtalk import extract_fullcontext

from voicevox_engine.full_context_label import Phoneme
from voicevox_engine.kana_parser import create_kana
from voicevox_engine.model import AudioQuery
from voicevox_engine.synthesis_engine.hts_engine_api_engine import (
    HtsEngineApiEngine,
    accent_phrase_to_phonemes,
)


class TestHtsEngineApiEngine(TestCase):
    def setUp(self) -> None:
        self.engine = HtsEngineApiEngine(speakers="", supported_devices="")
        self.text = "そういえば、あれってどうなったんでしたっけ?そうですか。分かりました。"
        self.accent_phrase = self.engine.create_accent_phrases(self.text, 0)
        return super().setUp()

    def test_accent_phrase_to_phonemes(self):
        ojt_phoneme = [Phoneme.from_label(i) for i in extract_fullcontext(self.text)]
        test_phoneme = accent_phrase_to_phonemes(self.accent_phrase)
        # OpenJTalkのフルコンテキストラベルから非対応の情報を消去
        for i in ojt_phoneme:
            i.contexts["b1"] = "xx"
            i.contexts["b2"] = "xx"
            i.contexts["b3"] = "xx"
            i.contexts["c1"] = "xx"
            i.contexts["c2"] = "xx"
            i.contexts["c3"] = "xx"
            i.contexts["d1"] = "xx"
            i.contexts["d2"] = "xx"
            i.contexts["d3"] = "xx"
        ojt_label = [i.label for i in ojt_phoneme]
        test_label = [i.label for i in test_phoneme]
        self.assertEqual(ojt_label, test_label)

    def test_synthesis(self):
        self.engine.synthesis(
            AudioQuery(
                accent_phrases=self.accent_phrase,
                speedScale=1,
                pitchScale=0,
                intonationScale=1,
                volumeScale=1,
                prePhonemeLength=0.1,
                postPhonemeLength=0.1,
                outputSamplingRate=24000,
                outputStereo=False,
                kana=create_kana(self.accent_phrase),
            ),
            speaker_id=0,
        )

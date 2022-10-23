from unittest import TestCase
from voicevox_engine.model import AccentPhrase, Mora
from voicevox_engine.synthesis_engine import synthesis_engine_base
from voicevox_engine.dev.synthesis_engine import mock

class Test_gen(TestCase):
    def test_fcl(self):
        test_text = "彼女はその事件を、生き生きとした筆致で描写した。"
        utterance = synthesis_engine_base.extract_full_context_label(test_text)
        accent_phrases = [
                AccentPhrase(
                    moras=synthesis_engine_base.full_context_label_moras_to_moras(accent_phrase.moras),
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
                for i_accent_phrase, accent_phrase in enumerate(
                    breath_group.accent_phrases
                )
        ]
        regen = mock.accent_phrase_to_phonemes(accent_phrases)
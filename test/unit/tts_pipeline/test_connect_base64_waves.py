"""connect_base64_waves 関数の単体テスト。"""

import base64
import io

import numpy as np
import numpy.testing
import pytest
import soundfile
from numpy.typing import NDArray
from soxr import resample

from voicevox_engine.tts_pipeline.connect_base64_waves import (
    ConnectBase64WavesException,
    connect_base64_waves,
)


def _generate_sine_wave_ndarray(
    seconds: float, samplerate: int, frequency: float
) -> NDArray[np.float32]:
    x = np.linspace(0, seconds, int(seconds * samplerate), endpoint=False)
    wave: NDArray[np.float32] = np.sin(2 * np.pi * frequency * x).astype(np.float32)

    return wave


def _encode_bytes(wave_ndarray: NDArray[np.float32], samplerate: int) -> bytes:
    wave_bio = io.BytesIO()
    soundfile.write(
        file=wave_bio,
        data=wave_ndarray,
        samplerate=samplerate,
        format="WAV",
        subtype="FLOAT",
    )
    wave_bio.seek(0)

    return wave_bio.getvalue()


def _generate_sine_wave_bytes(
    seconds: float, samplerate: int, frequency: float
) -> bytes:
    wave_ndarray = _generate_sine_wave_ndarray(seconds, samplerate, frequency)
    return _encode_bytes(wave_ndarray, samplerate)


def _encode_base64(wave_bytes: bytes) -> str:
    return base64.standard_b64encode(wave_bytes).decode("utf-8")


def _generate_sine_wave_base64(
    seconds: float, samplerate: int, frequency: float
) -> str:
    wave_bytes = _generate_sine_wave_bytes(seconds, samplerate, frequency)
    wave_base64 = _encode_base64(wave_bytes)
    return wave_base64


def test_connect() -> None:
    samplerate = 1000
    wave = _generate_sine_wave_ndarray(seconds=2, samplerate=samplerate, frequency=10)
    wave_base64 = _encode_base64(_encode_bytes(wave, samplerate=samplerate))

    wave_x2_ref = np.concatenate([wave, wave])

    wave_x2, _ = connect_base64_waves(waves=[wave_base64, wave_base64])

    assert wave_x2_ref.shape == wave_x2.shape

    assert (wave_x2_ref == wave_x2).all()


def test_no_wave_error() -> None:
    with pytest.raises(ConnectBase64WavesException):
        connect_base64_waves(waves=[])


def test_invalid_base64_error() -> None:
    wave_1000hz = _generate_sine_wave_base64(seconds=2, samplerate=1000, frequency=10)
    wave_1000hz_broken = wave_1000hz[1:]  # remove head 1 char

    with pytest.raises(ConnectBase64WavesException):
        connect_base64_waves(waves=[wave_1000hz_broken])


def test_invalid_wave_file_error() -> None:
    wave_1000hz = _generate_sine_wave_bytes(seconds=2, samplerate=1000, frequency=10)
    wave_1000hz_broken_bytes = wave_1000hz[1:]  # remove head 1 byte
    wave_1000hz_broken = _encode_base64(wave_1000hz_broken_bytes)

    with pytest.raises(ConnectBase64WavesException):
        connect_base64_waves(waves=[wave_1000hz_broken])


def test_different_frequency() -> None:
    wave_24000hz = _generate_sine_wave_ndarray(
        seconds=1, samplerate=24000, frequency=10
    )
    wave_1000hz = _generate_sine_wave_ndarray(seconds=2, samplerate=1000, frequency=10)
    wave_24000_base64 = _encode_base64(_encode_bytes(wave_24000hz, samplerate=24000))
    wave_1000_base64 = _encode_base64(_encode_bytes(wave_1000hz, samplerate=1000))

    wave_1000hz_to24000hz = resample(wave_1000hz, 1000, 24000)
    wave_x2_ref = np.concatenate([wave_24000hz, wave_1000hz_to24000hz])

    wave_x2, _ = connect_base64_waves(waves=[wave_24000_base64, wave_1000_base64])

    assert wave_x2_ref.shape == wave_x2.shape
    numpy.testing.assert_array_almost_equal(wave_x2_ref, wave_x2)


def test_different_channels() -> None:
    wave_1000hz = _generate_sine_wave_ndarray(seconds=2, samplerate=1000, frequency=10)
    wave_2ch_1000hz = np.array([wave_1000hz, wave_1000hz]).T
    wave_1ch_base64 = _encode_base64(_encode_bytes(wave_1000hz, samplerate=1000))
    wave_2ch_base64 = _encode_base64(_encode_bytes(wave_2ch_1000hz, samplerate=1000))

    wave_x2_ref = np.concatenate([wave_2ch_1000hz, wave_2ch_1000hz])

    wave_x2, _ = connect_base64_waves(waves=[wave_1ch_base64, wave_2ch_base64])

    assert wave_x2_ref.shape == wave_x2.shape
    assert (wave_x2_ref == wave_x2).all()

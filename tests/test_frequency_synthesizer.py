"""Unit tests for FrequencySynthesizer.

__init__ binds ZeroMQ sockets, so the tests build the object without running it
and inject a recording socket. That keeps the tuning arithmetic under test
without opening a single port.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frequency_synthesizer import FrequencySynthesizer


class RecordingSocket:
    """Stands in for the ZMQ PUB socket and keeps what was sent."""

    def __init__(self):
        self.sent = []

    def send_multipart(self, parts):
        self.sent.append(parts)


@pytest.fixture
def synth():
    s = FrequencySynthesizer.__new__(FrequencySynthesizer)
    s.center_freq = None
    s.doppler_offset = 0
    s.cmd_socket = RecordingSocket()
    return s


class TestEffectiveFrequency:
    def test_is_the_centre_frequency_when_there_is_no_shift(self, synth):
        synth.center_freq = 437_000_000

        assert synth._effective_frequency() == 437_000_000

    def test_adds_a_positive_doppler_shift(self, synth):
        synth.center_freq = 437_000_000
        synth.doppler_offset = 9_500

        assert synth._effective_frequency() == 437_009_500

    def test_subtracts_a_negative_doppler_shift(self, synth):
        synth.center_freq = 437_000_000
        synth.doppler_offset = -9_500

        assert synth._effective_frequency() == 436_990_500


class TestSendTune:
    def test_nothing_is_sent_before_a_centre_frequency_is_set(self, synth):
        synth._send_tune()

        assert synth.cmd_socket.sent == []

    def test_sends_the_tune_topic_and_the_effective_frequency(self, synth):
        synth.center_freq = 145_900_000
        synth.doppler_offset = 2_500

        synth._send_tune()

        assert synth.cmd_socket.sent == [[b"tune", b"145902500"]]

    def test_each_call_sends_one_message(self, synth):
        synth.center_freq = 437_000_000

        synth._send_tune()
        synth._send_tune()

        assert len(synth.cmd_socket.sent) == 2

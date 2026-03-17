# GRS Frequency Synthesizer

## Overview

The Frequency Synthesizer is an internal component of the Ground Station software pipeline. It sits between the Station Manager and the IQ Receiver, responsible for computing the effective tuning frequency at any given moment by combining the base center frequency with a Doppler correction offset, and forwarding the result to the IQ Receiver as a tune command.

The IQ Receiver is autonomous and does not depend on the Frequency Synthesizer to operate, it simply reacts to tune commands whenever they arrive. The Frequency Synthesizer is an optional layer that handles the Doppler correction math on top, as well as any changes in the center frequency.

## Dependencies

- Python 3
- `pyzmq`

## Usage

The `FrequencySynthesizer` class is not meant to be run standalone. It is instantiated and managed by the Station Manager:

```python
from frequency_synthesizer import FrequencySynthesizer

synth = FrequencySynthesizer(
    iq_receiver_socket_address="tcp://*:5557",
    station_manager_pub_address="tcp://localhost:5558"
)
synth.run()
```

To stop it gracefully:

```python
synth.stop()
```

## ZMQ Interface

### Subscribed topics (from Station Manager)

| Topic     | Payload        | Description                                      |
|-----------|----------------|--------------------------------------------------|
| `freq`    | Frequency (Hz) | Sets a new base center frequency                 |
| `doppler` | Offset (Hz)    | Updates the Doppler offset applied on top of the base frequency |

### Published topics (to IQ Receiver)

| Topic  | Payload        | Description                                         |
|--------|----------------|-----------------------------------------------------|
| `tune` | Frequency (Hz) | Effective frequency (`center_freq + doppler_offset`) to tune the SDR to |

## Behavior

- On startup, `center_freq` is `None`. The synthesizer will not send any tune command until the Station Manager sends a `freq` command.
- If a `doppler` command arrives before any `freq` command has been received, it is ignored and a warning is printed.
- Doppler offset defaults to 0 and is updated whenever a `doppler` command is received.
- The effective frequency sent to the IQ Receiver is always `center_freq + doppler_offset`.
- It is the Station Manager's responsibility to ensure the initial `center_freq` matches the frequency the IQ Receiver was started with.

## Notes

- The Frequency Synthesizer does not compute Doppler shifts itself. It expects the Station Manager (or a dedicated propagator module) to supply pre-computed Doppler offsets.
- Both constructor addresses should be kept consistent with the corresponding addresses configured in the IQ Receiver and Station Manager.

<h1 align="center">
    GRS Frequency Synthesizer
    <br>
</h1>

<h4 align="center">Frequency Synthesizer of the SpaceLab's Ground Station.</h4>

<p align="center">
    <a href="https://github.com/spacelab-ufsc/grs-frequency-synthesizer">
        <img src="https://img.shields.io/badge/status-development-green?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/grs-frequency-synthesizer/releases">
        <img alt="GitHub commits since latest release (by date)" src="https://img.shields.io/github/commits-since/spacelab-ufsc/grs-frequency-synthesizer/latest?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/grs-frequency-synthesizer/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/license-GPL3-yellow?style=for-the-badge">
    </a>
</p>

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#dependencies">Dependencies</a> •
    <a href="#usage">Usage</a> •
    <a href="#documentation">Documentation</a> •
    <a href="#license">License</a>
</p>

## Overview

The GRS Frequency Synthesizer is an internal component of SpaceLab's Ground Station software pipeline. It sits between the Station Manager and the IQ Receiver, responsible for computing the effective tuning frequency at any given moment by combining the base center frequency with a Doppler correction offset, and forwarding the result to the IQ Receiver as a tune command.

The IQ Receiver is autonomous and does not depend on the Frequency Synthesizer to operate — it simply reacts to tune commands whenever they arrive. The Frequency Synthesizer is an optional layer that handles the Doppler correction math on top, as well as any changes in the center frequency.

## Dependencies

* [pyzmq](https://pypi.org/project/pyzmq/)

### Installation

```pip install pyzmq```

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

### ZMQ Interface

Subscribed topics (from Station Manager):

| Topic     | Payload        | Description                                                             |
|-----------|----------------|-------------------------------------------------------------------------|
| `freq`    | Frequency (Hz) | Sets a new base center frequency                                        |
| `doppler` | Offset (Hz)    | Updates the Doppler offset applied on top of the base frequency         |

Published topics (to IQ Receiver):

| Topic  | Payload        | Description                                                             |
|--------|----------------|-------------------------------------------------------------------------|
| `tune` | Frequency (Hz) | Effective frequency (`center_freq + doppler_offset`) to tune the SDR to |

### Behavior

- On startup, `center_freq` is `None`. The synthesizer will not send any tune command until the Station Manager sends a `freq` command.
- If a `doppler` command arrives before any `freq` command has been received, it is ignored and a warning is printed.
- Doppler offset defaults to 0 and is updated whenever a `doppler` command is received.
- The effective frequency sent to the IQ Receiver is always `center_freq + doppler_offset`.
- It is the Station Manager's responsibility to ensure the initial `center_freq` matches the frequency the IQ Receiver was started with.

> **Note:** The Frequency Synthesizer does not compute Doppler shifts itself. It expects the Station Manager (or a dedicated propagator module) to supply pre-computed Doppler offsets.

## Documentation

The documentation of this project is generated using the Sphinx tool, and it is available [here](https://spacelab-ufsc.github.io/grs-frequency-synthesizer/).

### Dependencies

* Sphinx
* sphinx-rtd-theme

### Building the Documentation

```make html```

## License

This project is licensed under GPLv3 license.

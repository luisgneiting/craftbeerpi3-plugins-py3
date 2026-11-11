# craftbeerpi3-plugins-py3

Plugins for [CraftBeerPi3](https://github.com/Manuel83/craftbeerpi3), updated for **Python 3.13 / Flask 3** running on **Raspberry Pi OS 13 (Trixie)**.

Compatible with the [`python3-flask3-compat`](https://github.com/luisgneiting/craftbeerpi3/tree/python3-flask3-compat) fork.

---

## Plugin compatibility

| Plugin | Python 3 | Notes |
|--------|----------|-------|
| `gpio_actor` | ✅ | Works via `rpi-lgpio` (drop-in `RPi.GPIO` for Raspberry Pi OS 13) |
| `PIDBoil` | ✅ | No changes needed |
| `PIDAutoTune` | ✅ | Minor fix: `dict.keys()` → `list` |
| `fermenter_hysteresis` | ✅ | No changes needed |
| `ARCHIVED/AmazonAlexaPlugin` | ⚠️ | Syntax fixed for Python 3, but `flask_ask` is unmaintained for Flask 3 |

---

## Installation

Clone this repo into the `modules/plugins` directory of your CraftBeerPi3 installation:

```bash
cd /home/otavio/craftbeerpi3/modules
git clone https://github.com/luisgneiting/craftbeerpi3-plugins-py3 plugins
```

> **Note:** This replaces the entire `plugins/` directory. If you have custom plugins there, back them up first.

To update later:

```bash
cd /home/otavio/craftbeerpi3/modules/plugins
git pull
```

Then restart the service:

```bash
sudo systemctl restart craftbeerpi
```

---

## Plugin descriptions

### gpio_actor
Provides four actor types for controlling GPIO pins:
- **GPIOSimple** — digital on/off
- **GPIOPWM** — hardware PWM with configurable frequency and duty cycle
- **RelayBoard** — inverted logic (relay boards that use active-low)
- **Dummy** — no-op actor for testing

Requires `rpi-lgpio` (included in Raspberry Pi OS 13):
```bash
pip3 install rpi-lgpio
```

### PIDBoil
PID controller with a boil-threshold mode. Runs a standard Arduino-style PID loop for kettle temperature, but switches to full power (100%) when the target temperature is at or above a configurable boil threshold.

Parameters: P, I, D, max output %, boil threshold.

### PIDAutoTune
Automatically calculates optimal PID parameters using relay feedback oscillation (Ziegler-Nichols method). Supports multiple tuning rules: `ziegler-nichols`, `tyreus-luyben`, `ciancone-marlin`, `pessen-integral`, `some-overshoot`, `no-overshoot`, `brewing`.

Outputs Kp/Ki/Kd values as CraftBeerPi notifications when tuning completes.

### fermenter_hysteresis
Hysteresis controller for fermenters with independent heater and cooler control. Maintains fermentation temperature using configurable offset pairs for heater on/off and cooler on/off.

---

## Archived plugins

### ARCHIVED/AmazonAlexaPlugin
Amazon Alexa voice interface for CraftBeerPi3. Python 3 syntax has been corrected (`print` statements, `iteritems()` → `items()`), but the `flask_ask` dependency is unmaintained and incompatible with Flask 3.

Archived until a compatible Alexa Skills Kit integration is available.

---

## Requirements

- Python 3.11+
- Flask 3.x
- CraftBeerPi3 fork: [`luisgneiting/craftbeerpi3`](https://github.com/luisgneiting/craftbeerpi3) (branch `python3-flask3-compat`)
- Raspberry Pi OS 13 (Trixie) — or any system with `rpi-lgpio` for GPIO support

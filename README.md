# Ninebot Scooter integration for Home Assistant

Connects to and polls data from a Ninebot (Segway) eKickScooter over Bluetooth Low Energy (BLE),
using the [ninebot-ble](https://github.com/WalkTheEarth/ninebot-ble) library.

Both newer encrypted-firmware and older plain (legacy) firmware scooters are supported — the
protocol is detected automatically on connect. The client is read-only: it never writes to the
scooter, and pairing is per-session only.

## Supported scooters

Model detection is based on the serial number and covers the Ninebot E-series (E22/E25/E45),
older ES-series (ES1–ES4, SNSC1.x), the Max family (G30/G30D/G30E/G30LP/G30LE/G30LD, SNSC2.x
rentals, Seat Mó, Audi EKS), the F-series (F20–F60), the ES3 Plus, and the x3 generation at
family level (`1TE` → E3 / E3 Pro, `1CG` → Max G3). Unknown serials degrade gracefully to
`<series>-series`.

Scooters are discovered advertising the classic Ninebot manufacturer id `0x424E` (16974), the
newer `0x434E` (17230) with a serial-style broadcast name (e.g. `1TEFE2517C0419`), or the
serial-style name alone.

Registers a particular model or firmware does not implement are skipped instead of failing the
whole update, so partial data from unusual models is still reported.

## Requirements note

The integration requires the `ninebot-bleNG` Python package (version pinned in the
[manifest](custom_components/ninebot_scooter/manifest.json); the importable module is
`ninebot_ble`). It is published on PyPI via this repository's GitHub Actions tag workflow
([PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/)). Install it manually into
Home Assistant's Python environment first:

```
pip install ninebot-bleNG
```

(For a Home Assistant Container/Core install, run this inside the container/venv Home Assistant
uses; the version must match the manifest pin or the setup fails its requirements check. On Home
Assistant OS the environment is read-only — use a container or venv install, or wait for a PyPI
release.)

## Installation

### HACS

This repository ships a `hacs.json` and can be added as a custom repository in
[HACS](https://hacs.xyz/) (category: Integration). The requirements note above still applies.

### Manual

1. Copy the directory `custom_components/ninebot_scooter` into your installation under
   `<config_dir>/custom_components`.

2. Restart Home Assistant.

## Configuration

Scooters are discovered automatically when they are broadcasting. To add one manually, use
**Settings → Devices & Services → Add Integration → Ninebot Scooter**.

Data updates only while the scooter is awake and advertising (BLE poll on advertisement). If the
scooter is idle/asleep, short-press its power button to wake it.

First connection performs the session pairing: when the scooter asks for confirmation, press the
power button on the scooter once (the same confirm ScooterHacking Utility does). Unloading or
removing the config entry disconnects the scooter.

## Entities

The integration creates the device `Ninebot <model>` and one sensor per available register,
for example:

- Battery: level (%), voltage (V), current (A), temperature 1 and 2 (°C), remaining capacity
  (mAh), factory capacity, health (%), balancing/overvoltage/undervoltage states
- Riding: total mileage (km), total riding time (h), total operation time (h), single mileage
  (km), single operation time (h), actual and predicted remaining mileage (km), average speed
  (km/h)
- State: operating mode (eco/normal/sport), error code, alarm code, speed limits (km/h), cruise
  control, tail light, buzzer, speed-limited/locked/activated flags
- Hardware: scooter temperature (°C), controller supply voltage (V), controller/BMS/BLE firmware
  versions, serial numbers

Measurable quantities carry `state_class: measurement`, so they feed Home Assistant's long-term
statistics.

## Troubleshooting

Enable debug logging for the library and the integration via `configuration.yaml`:

```yaml
logger:
  logs:
    ninebot_ble: debug
    custom_components.ninebot_scooter: debug
```

- **Scooter not discovered** — wake it with a short press of the power button (it stops
  advertising when idle), keep it in range, and make sure no other app is holding the BLE
  connection.
- **Setup fails with a requirements error** — see the requirements note above: install
  `ninebot-bleNG` into Home Assistant's Python environment manually.
- **Stuck waiting for pairing** — press the scooter's power button once when prompted; the client
  waits up to 60 seconds.
- **Bluetooth proxies** — the integration *connects* to the scooter (not just listening), so a
  proxy must support active connections (ESP32-based ESPHome Bluetooth proxies do; also keep the
  proxy firmware current).

## Credits

Based on [ownbee/ninebot-integration](https://github.com/ownbee/ninebot-integration) with the
[forked ninebot-ble](https://github.com/WalkTheEarth/ninebot-ble) library (protocol knowledge from
[miauth](https://github.com/dnandha/miauth) and the
[ScooterHacking.org wiki](https://wiki.scooterhacking.org/)). Fixes and model support in this fork
were verified against real hardware.

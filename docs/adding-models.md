# Adding support for a new scooter model

This project aims to support as many Ninebot scooters as possible. Most models work out of the
box because they share the same protocol and register layout; the model-specific parts are
concentrated in two places. This guide shows where to add what, and how to verify against real
hardware.

## What usually needs no changes

- **Connection, handshake and register reads** — the encrypted protocol (miauth-based) and the
  legacy plain protocol are auto-detected, so a new model normally needs no transport work.
- **Register decoding** — all models share the register tables; unsupported registers are skipped
  automatically instead of failing the update.

## 1. Discovery: `is_scooter_advertisement()`

If a new model does not show up in Home Assistant at all, it probably advertises a signature we
do not know. Check the scooter's advertisement (e.g. with a BLE scanner app or `bluetoothctl`):

- Classic generations: manufacturer id `0x424E` (16974), name like `NBScooter...`
- Newer generations: manufacturer id `0x434E` (17230), serial-style name (e.g. `1TEFE2517C0419`)
- Some models: no manufacturer data at all, only the serial-style name

Add new manufacturer ids to `NINEBOT_MANUFACTURER_IDS` in `ninebot-ble/ninebot_ble/const.py`,
and adjust the name heuristic in `ninebot-ble/ninebot_ble/util.py` if the new name shape is not
matched. Mirror the ids in the integration's
[`manifest.json`](../custom_components/ninebot_scooter/manifest.json) (`bluetooth` list).

## 2. Model detection: `SerialParser`

The device name comes from the serial number parser in
[`ninebot-ble/ninebot_ble/serial_parser.py`](https://github.com/WalkTheEarth/ninebot-ble/blob/main/ninebot_ble/serial_parser.py):

- New model series (first three serial characters): add an entry to `ProductSeries` and its
  display name to `SERIES_NAMES`.
- New variant letter within a known series: add a `"<letter>": "<model name>"` entry to the
  series' dict in `PRODUCT_VERSION_MAPPING`. If the letters are not documented anywhere, leave
  the dict empty — the parser then shows the family name instead of guessing.
- Sources for the mappings: the ScooterHacking.org wiki (nbeseries, nbesx, nbmax, nbfseries) and
  community documentation. Never invent a mapping; an honest family-level name beats a wrong
  model name.

The serial anatomy (year/week/revision positions) is documented in
[ninebot-ble's protocol notes](https://github.com/WalkTheEarth/ninebot-ble/blob/main/docs/protocol.md).

## 3. Register scaling quirks

A few registers are scaled differently on some models (a known example: "total operation time",
which is clearly wrong on at least one x3-generation model). If a value looks wrong compared with
ScooterHacking Utility:

1. Read the raw value with the CLI (`ninebot-ble --total-operation-time`) and note the scaling
   the table applies (see `ninebot-ble/ninebot_ble/register.py`).
2. Compare with what SHU reports for the same state (charge the scooter / ride a bit to get
   changing values).
3. If the model diverges, add a model-conditional scaler rather than changing the table for all
   models — open an issue first so the condition can be chosen to match real hardware evidence.

## 4. Verification checklist

- [ ] `pip install -e ninebot-ble && python -m pytest` passes offline
- [ ] `ninebot-ble` discovers and connects to the new model, pairing confirm works
- [ ] Register dump matches what ScooterHacking Utility reports (battery %, voltage, mileage,
      temperature)
- [ ] Device title shows the correct model name
- [ ] HA integration discovers the scooter and creates sensors without errors in the log

Report results (positive and negative) in an issue — community-verified models are how this
project's model table grows.

# Ninebot Scooter integration for Home Assistant

Connects to and polls data from a Ninebot Scooter using BLE.

**NOTE: This is integration has some known bugs in it and is in an alpha state. It is also a bit stale in development due to lack of mainatiner time. Feel free to fork or help pushing PRs improving this integration.**

## Supported scooters

Both newer encrypted-firmware and older plain (legacy) firmware scooters are supported — the
protocol is detected automatically on connect. Model detection via serial number covers the
Ninebot E-series, older ES-series (ES1–ES4), the Max family (G30/G30LP and rentals), the
F-series and more. Registers a particular model does not implement are skipped instead of
failing the whole update.

## Manual installation

1. Copy the directory `custom_components/ninebot_scooter` into you installation under
   `<config_dir>/custom_components`.

2. Restart home assistant.

## HACS installation

This repository ships a `hacs.json` and can be added as a custom repository in
[HACS](https://hacs.xyz/).

## Scooters found

Scooters are discovered automatically when they are broadcasting (manufacturer id `16974`), or
can be added manually via **Settings → Devices & Services → Add Integration → Ninebot Scooter**.

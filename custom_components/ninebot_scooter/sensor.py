"""Support for sensors."""
from __future__ import annotations

from typing import Any

from ninebot_ble import SensorUpdate

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorCoordinator,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .const import DOMAIN
from .device import device_key_to_bluetooth_entity_key

# Device classes that map cleanly onto HA's MEASUREMENT state class, enabling
# long-term statistics for those entities.
_MEASUREMENT_DEVICE_CLASSES = {
    SensorDeviceClass.BATTERY,
    SensorDeviceClass.CURRENT,
    SensorDeviceClass.POWER,
    SensorDeviceClass.SPEED,
    SensorDeviceClass.TEMPERATURE,
    SensorDeviceClass.VOLTAGE,
}


def _safe_device_class(device_class: Any) -> SensorDeviceClass | None:
    """Convert a sensor_state_data device class to a HA one, if known.

    Newer ninebot-ble releases may know device classes this HA version does
    not; degrade to a unit-less sensor instead of crashing setup.
    """
    if device_class is None:
        return None
    try:
        return SensorDeviceClass(device_class)
    except ValueError:
        return None


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""

    entity_descriptions = {}
    for device_key, desc in sensor_update.entity_descriptions.items():
        device_class = _safe_device_class(desc.device_class)
        entity_descriptions[device_key_to_bluetooth_entity_key(device_key)] = SensorEntityDescription(
            key=str(device_key),
            device_class=device_class,
            native_unit_of_measurement=desc.native_unit_of_measurement,
            state_class=SensorStateClass.MEASUREMENT
            if device_class in _MEASUREMENT_DEVICE_CLASSES
            else None,
        )

    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions=entity_descriptions,
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ninebot sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][entry.entry_id]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(processor.async_add_entities_listener(NinebotBluetoothSensorEntity, async_add_entities))
    entry.async_on_unload(coordinator.async_register_processor(processor, SensorEntityDescription))


class NinebotBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[PassiveBluetoothDataProcessor[str | int | None]],
    SensorEntity,
):
    """Representation of a Ninebot sensor."""

    @property
    def native_value(self) -> str | int | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)

    @property
    def available(self) -> bool:
        """Return True if entity is available.

        The sensor is only created when the device is seen.

        Since these are sleepy devices which stop broadcasting
        when not in use, we can't rely on the last update time
        so once we have seen the device we always return True.
        """
        return True

    @property
    def assumed_state(self) -> bool:
        """Return True if the device is no longer broadcasting."""
        return not self.processor.available

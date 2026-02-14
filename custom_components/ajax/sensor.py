from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
from .device_mapper import map_ajax_device
from .api import AjaxAPI
import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    devices_by_hub = hass.data[DOMAIN][entry.entry_id]["devices_by_hub"]
    entities = []
    data = hass.data[DOMAIN][entry.entry_id]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    for hub_id, devices in devices_by_hub.items():
        for device in devices:
            for platform, meta in map_ajax_device(device):
                if platform != "sensor":
                    continue
                if meta.get("device_class") == "temperature":
                    entity = FireProtectSensor(device, meta, hub_id, api)
                elif meta.get("device_class") == "door_temperature":
                    entity = DoorProtectSensor(device, meta, hub_id, api)  
                elif meta.get("device_class") == "motion_temperature":
                    entity = MotionProtectSensor(device, meta, hub_id, api)              
                else:
                    entity = AjaxSensor(device, meta, hub_id, api)
                entities.append(entity)

    async_add_entities(entities)


class AjaxSensor(SensorEntity):
    def __init__(self, device, meta, hub_id, api):
        self._device = device
        self.hub_id = hub_id
        self._meta = meta
        self._attr_name = device.get("deviceName") + f" ({device.get('id')})"
        self._attr_unique_id = f"ajax_{device.get('id')}_{meta.get('device_class')}"
        self._attr_device_class = meta.get("device_class")
        self._attr_native_unit_of_measurement = meta.get("unit")
        self.api = api
        self._battery = None
        self._native_value = None
        _LOGGER.error("AJAX device data - DENTRO SENSOR: %s", self._device)
        _LOGGER.error("Mapped meta - DENTRO SENSOR: %s", self._meta)

    @property
    def native_value(self):     
        return self._native_value
    @property
    def extra_state_attributes(self):
        return {
            "battery_level": self._battery,
        }

    async def async_update(self):
        device_info = await self.api.get_device_info(self.hub_id, self._device.get('id'))
        self._battery = device_info.get('batteryChargeLevelPercentage')

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"ajax_{self._device.get('id')}_{self._meta.get('device_class')}")},
            "name": self._attr_name,
            "manufacturer": "Ajax",
            "model": self._meta.get("device_class", "Unknown"),
        }
      



class FireProtectSensor(AjaxSensor):
    def __init__(self, device, meta, hub_id, api):
        super().__init__(device, meta, hub_id, api)
        self._temperature = None


    @property
    def native_value(self):
        return self._temperature

    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes.copy()
        return attrs

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"ajax_{self._device.get('id')}")},
            "name": "Ajax FireProtectPlus",
            "manufacturer": "Ajax",
            "model": "FireProtectPlus",
        }

    async def async_update(self):
        await super().async_update() # updating in parent class
        device_info = await self.api.get_device_info(self.hub_id, self._device.get('id'))
        self._temperature = device_info.get('temperature')

            
            
class DoorProtectSensor(AjaxSensor):
    def __init__(self, device, meta, hub_id, api):
        super().__init__(device, meta, hub_id, api)
        self._temperature = None
         # INIZIALIZZA QUI i valori usati in device_info
        self._name_from_api = self._attr_name  # valore di fallback
        self._model_version = device.get("device_class", "DoorProtect")
        self._firmware_version = device.get("firmwareVersion", "0")
        self._serial_number = device.get("id", "0")
        _LOGGER.error("AJAX device data - DENTRO DOORPROTEC: %s", self._device)
        _LOGGER.error("Mapped meta - DENTRO DOORPROTEC: %s", self._meta)

    @property
    def native_value(self):
        return self._temperature


    async def async_update(self):
        await super().async_update() # updating in parent class
        device_info = await self.api.get_device_info(self.hub_id, self._device.get('id'))
        # Salva i campi che ti interessano
        self._name_from_api = device_info.get('deviceName')
        #self._model_version = device_info.get('deviceType')
        self._temperature = device_info.get('temperature')
        self._firmware_version = device_info.get('firmwareVersion')
        #self._serial_number = device_info.get('id')
        _LOGGER.error("AJAX device data - DENTRO DOORPROTEC: %s", self._device)
        _LOGGER.error("Mapped meta - DENTRO DOORPROTEC: %s", self._meta)
        
        # Se l’API fornisce hw data



    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"ajax_{self._device.get('id')}")},
            "via_device": (DOMAIN, f"ajax_hub_{self.hub_id}"),  # <–– qui!
            "name": self._name_from_api,
            "manufacturer": "Ajax",
            "model": self._model_version,
            "sw_version": self._firmware_version,
            "serial_number": self._serial_number,
            _LOGGER.error("AJAX device data - DENTRO DOORPROTEC: %s", self._device)
            _LOGGER.error("Mapped meta - DENTRO DOORPROTEC: %s", self._meta)
        }

class MotionProtectSensor(AjaxSensor):
    def __init__(self, device, meta, hub_id, api):
        super().__init__(device, meta, hub_id, api)
        self._temperature = None

    @property
    def native_value(self):
        return self._temperature


    async def async_update(self):
        await super().async_update() # updating in parent class
        device_info = await self.api.get_device_info(self.hub_id, self._device.get('id'))
        self._temperature = device_info.get('temperature')


    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"ajax_{self._device.get('id')}")},
            "name": "Ajax MotionProtect",
            "manufacturer": "Ajax",
            "model": "MotionProtect",
        }

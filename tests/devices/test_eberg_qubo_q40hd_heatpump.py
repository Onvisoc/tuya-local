from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_DRY,
    CURRENT_HVAC_FAN,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_SLEEP,
    PRESET_COMFORT,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_OFF,
    SWING_VERTICAL,
)
from homeassistant.const import (
    STATE_UNAVAILABLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TIME_HOURS,
)

from ..const import EBERG_QUBO_Q40HD_PAYLOAD
from ..helpers import assert_device_properties_set
from ..mixins.climate import TargetTemperatureTests
from ..mixins.number import BasicNumberTests
from .base_device_tests import TuyaDeviceTestCase

POWER_DPS = "1"
TEMPERATURE_DPS = "2"
CURRENTTEMP_DPS = "3"
HVACMODE_DPS = "4"
FAN_DPS = "5"
UNIT_DPS = "19"
TIMER_DPS = "22"
PRESET_DPS = "25"
SWING_DPS = "30"
HVACACTION_DPS = "101"


class TestEbergQuboQ40HDHeatpump(
    BasicNumberTests, TargetTemperatureTests, TuyaDeviceTestCase
):
    __test__ = True

    def setUp(self):
        self.setUpForConfig(
            "eberg_qubo_q40hd_heatpump.yaml",
            EBERG_QUBO_Q40HD_PAYLOAD,
        )
        self.subject = self.entities.get("climate")
        self.setUpTargetTemperature(
            TEMPERATURE_DPS,
            self.subject,
            min=17,
            max=30,
        )
        self.setUpBasicNumber(
            TIMER_DPS,
            self.entities.get("number_timer"),
            max=24,
            unit=TIME_HOURS,
        )
        self.mark_secondary(["number_timer"])

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            (
                SUPPORT_TARGET_TEMPERATURE
                | SUPPORT_FAN_MODE
                | SUPPORT_PRESET_MODE
                | SUPPORT_SWING_MODE
            ),
        )

    def test_icon(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "cold"
        self.assertEqual(self.subject.icon, "mdi:snowflake")
        self.dps[HVACMODE_DPS] = "hot"
        self.assertEqual(self.subject.icon, "mdi:fire")
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:hvac-off")

    def test_temperature_unit(self):
        self.dps[UNIT_DPS] = "c"
        self.assertEqual(self.subject.temperature_unit, TEMP_CELSIUS)
        self.dps[UNIT_DPS] = "f"
        self.assertEqual(self.subject.temperature_unit, TEMP_FAHRENHEIT)

    def test_minimum_target_temperature_f(self):
        self.dps[UNIT_DPS] = "f"
        self.assertEqual(self.subject.min_temp, 63)

    def test_maximum_target_temperature_f(self):
        self.dps[UNIT_DPS] = "f"
        self.assertEqual(self.subject.max_temp, 86)

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DPS] = 25
        self.assertEqual(self.subject.current_temperature, 25)

    def test_hvac_mode(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "cold"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_COOL)

        self.dps[HVACMODE_DPS] = "hot"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_HEAT)

        self.dps[HVACMODE_DPS] = None
        self.assertEqual(self.subject.hvac_mode, STATE_UNAVAILABLE)

        self.dps[HVACMODE_DPS] = "cold"
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_OFF)

    def test_hvac_modes(self):
        self.assertCountEqual(
            self.subject.hvac_modes,
            [
                HVAC_MODE_OFF,
                HVAC_MODE_COOL,
                HVAC_MODE_HEAT,
            ],
        )

    async def test_turn_on(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "cold"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_COOL)

    async def test_turn_off(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: False}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_OFF)

    def test_fan_mode(self):
        self.dps[FAN_DPS] = "low"
        self.assertEqual(self.subject.fan_mode, "low")
        self.dps[FAN_DPS] = "middle"
        self.assertEqual(self.subject.fan_mode, "medium")
        self.dps[FAN_DPS] = "high"
        self.assertEqual(self.subject.fan_mode, "high")
        self.dps[FAN_DPS] = "auto"
        self.assertEqual(self.subject.fan_mode, "auto")

    def test_fan_modes(self):
        self.assertCountEqual(
            self.subject.fan_modes,
            [
                "auto",
                "low",
                "medium",
                "high",
            ],
        )

    async def test_set_fan_mode_to_low(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: "low"},
        ):
            await self.subject.async_set_fan_mode("low")

    async def test_set_fan_mode_to_medium(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: "middle"},
        ):
            await self.subject.async_set_fan_mode("medium")

    async def test_set_fan_mode_to_high(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: "high"},
        ):
            await self.subject.async_set_fan_mode("high")

    async def test_set_fan_mode_to_auto(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: "auto"},
        ):
            await self.subject.async_set_fan_mode("auto")

    def test_swing_mode(self):
        self.dps[SWING_DPS] = True
        self.assertEqual(self.subject.swing_mode, SWING_VERTICAL)
        self.dps[SWING_DPS] = False
        self.assertEqual(self.subject.swing_mode, SWING_OFF)

    def test_swing_modes(self):
        self.assertCountEqual(
            self.subject.swing_modes,
            [
                SWING_VERTICAL,
                SWING_OFF,
            ],
        )

    async def test_set_swing_mode_to_vertical(self):
        async with assert_device_properties_set(
            self.subject._device,
            {SWING_DPS: True},
        ):
            await self.subject.async_set_swing_mode(SWING_VERTICAL)

    async def test_set_swing_mode_to_off(self):
        async with assert_device_properties_set(
            self.subject._device,
            {SWING_DPS: False},
        ):
            await self.subject.async_set_swing_mode(SWING_OFF)

    def test_preset_mode(self):
        self.dps[PRESET_DPS] = True
        self.assertEqual(self.subject.preset_mode, PRESET_SLEEP)
        self.dps[PRESET_DPS] = False
        self.assertEqual(self.subject.preset_mode, PRESET_COMFORT)

    def test_preset_modes(self):
        self.assertCountEqual(
            self.subject.preset_modes,
            [
                PRESET_COMFORT,
                PRESET_SLEEP,
            ],
        )

    async def test_set_preset_mode_to_sleep(self):
        async with assert_device_properties_set(
            self.subject._device,
            {PRESET_DPS: True},
        ):
            await self.subject.async_set_preset_mode(PRESET_SLEEP)

    async def test_set_preset_mode_to_normal(self):
        async with assert_device_properties_set(
            self.subject._device,
            {PRESET_DPS: False},
        ):
            await self.subject.async_set_preset_mode(PRESET_COMFORT)

    def test_hvac_action(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACACTION_DPS] = "heat_s"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_HEAT)

        self.dps[HVACACTION_DPS] = "hot"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_HEAT)

        self.dps[HVACACTION_DPS] = "heating"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_HEAT)

        self.dps[HVACACTION_DPS] = "cool_s"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_COOL)

        self.dps[HVACACTION_DPS] = "cooling"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_COOL)

        self.dps[HVACACTION_DPS] = "anti-clockwise"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_FAN)

        self.dps[HVACACTION_DPS] = "ventilation"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_FAN)

        self.dps[HVACACTION_DPS] = "wind"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_FAN)

        self.dps[HVACACTION_DPS] = "appointment"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_IDLE)

        self.dps[HVACACTION_DPS] = "auto"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_IDLE)

        self.dps[HVACACTION_DPS] = "auto_clean"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_IDLE)

        self.dps[HVACACTION_DPS] = "eco"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_IDLE)

        self.dps[HVACACTION_DPS] = "wet"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_DRY)

        self.dps[HVACACTION_DPS] = "off"
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_IDLE)

        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.hvac_action, CURRENT_HVAC_OFF)

    def test_extra_state_attributes(self):
        self.dps[TIMER_DPS] = 22
        self.assertDictEqual(
            self.subject.extra_state_attributes,
            {
                "timer": 22,
            },
        )

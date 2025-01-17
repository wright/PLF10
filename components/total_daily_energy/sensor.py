import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, time
from esphome.const import (
    CONF_ICON,
    CONF_ID,
    CONF_RESTORE,
    CONF_TIME_ID,
    DEVICE_CLASS_ENERGY,
    CONF_METHOD,
    STATE_CLASS_TOTAL_INCREASING,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ACCURACY_DECIMALS,
)
from esphome.core.entity_helpers import inherit_property_from

DEPENDENCIES = ["time"]

CONF_POWER_ID = "power_id"
CONF_MIN_SAVE_INTERVAL = "min_save_interval"
total_daily_energy_ns = cg.esphome_ns.namespace("total_daily_energy")
TotalDailyEnergyMethod = total_daily_energy_ns.enum("TotalDailyEnergyMethod")
TOTAL_DAILY_ENERGY_METHODS = {
    "trapezoid": TotalDailyEnergyMethod.TOTAL_DAILY_ENERGY_METHOD_TRAPEZOID,
    "left": TotalDailyEnergyMethod.TOTAL_DAILY_ENERGY_METHOD_LEFT,
    "right": TotalDailyEnergyMethod.TOTAL_DAILY_ENERGY_METHOD_RIGHT,
}
TotalDailyEnergy = total_daily_energy_ns.class_(
    "TotalDailyEnergy", sensor.Sensor, cg.Component
)


def inherit_unit_of_measurement(uom, config):
    return uom + "h"


def inherit_accuracy_decimals(decimals, config):
    return decimals + 2


CONFIG_SCHEMA = (
    sensor.sensor_schema(
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    )
    .extend(
        {
            cv.GenerateID(): cv.declare_id(TotalDailyEnergy),
            cv.GenerateID(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
            cv.Required(CONF_POWER_ID): cv.use_id(sensor.Sensor),
            cv.Optional(CONF_RESTORE, default=True): cv.boolean,
            cv.Optional(
                CONF_MIN_SAVE_INTERVAL, default="0s"
            ): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_METHOD, default="right"): cv.enum(
                TOTAL_DAILY_ENERGY_METHODS, lower=True
            ),
            cv.Optional("forced_hash"): cv.int_,
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)

FINAL_VALIDATE_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.use_id(TotalDailyEnergy),
            cv.Optional(CONF_ICON): cv.icon,
            cv.Optional(CONF_UNIT_OF_MEASUREMENT): sensor.validate_unit_of_measurement,
            cv.Optional(CONF_ACCURACY_DECIMALS): sensor.validate_accuracy_decimals,
            cv.Required(CONF_POWER_ID): cv.use_id(sensor.Sensor),
        },
        extra=cv.ALLOW_EXTRA,
    ),
    inherit_property_from(CONF_ICON, CONF_POWER_ID),
    inherit_property_from(
        CONF_UNIT_OF_MEASUREMENT, CONF_POWER_ID, transform=inherit_unit_of_measurement
    ),
    inherit_property_from(
        CONF_ACCURACY_DECIMALS, CONF_POWER_ID, transform=inherit_accuracy_decimals
    ),
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])

    await cg.register_component(var, config)
    await sensor.register_sensor(var, config)

    sens = await cg.get_variable(config[CONF_POWER_ID])
    cg.add(var.set_parent(sens))
    time_ = await cg.get_variable(config[CONF_TIME_ID])
    cg.add(var.set_time(time_))
    cg.add(var.set_restore(config[CONF_RESTORE]))
    cg.add(var.set_min_save_interval(config[CONF_MIN_SAVE_INTERVAL]))
    cg.add(var.set_method(config[CONF_METHOD]))

    if "forced_hash" in config:
        cg.add(var.set_forced_hash(config["forced_hash"]))

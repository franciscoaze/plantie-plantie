
class _Job(object):
    pass


class GrowLedON(_Job):
    id = "growled_on"
    trigger = "cron"
    trigger_args = {"hour": '9'}
    topic = "actions/growled"
    value = "255"
    value_legend = "pwm value"


class GrowLedOFF(_Job):
    id = "growled_off"
    trigger = "cron"
    trigger_args = {"hour": '15'}
    topic = "actions/growled"
    value = "0"
    value_legend = "pwm value"


class PumpTop(_Job):
    id = "pump1"
    trigger = "cron"
    trigger_args = {"day_of_week": '1,4', 'hour': '10'}
    topic = "actions/pump1"
    value = 3
    value_legend = "sec"


class PumpBottom(_Job):
    id = "pump2"
    trigger = "cron"
    trigger_args = {"day_of_week": "2,5", "hour": "10", "minute": "00"}
    topic = "actions/pump2"
    value = '40'
    value_legend = "sec"


class BmeSensor(_Job):
    id = "bme_sensor"
    trigger = "interval"
    trigger_args = {"minutes": '5'}
    topic = "sensors/requests/BME"
    value = "BME"
    value_legend = "type of sensor"
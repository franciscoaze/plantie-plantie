"""
This is the core script for the pyplantie framework.
The brains of the operation.
UI apps may communicate with this module but are able to send commands directly to the rwis.
Main goals:
    - Trigger events
    - Redirect sensor data to databases
    - Store config values
    - Should be able to kill or start new modules
"""
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BlockingScheduler
import logging
import importlib, inspect
from pyplantie.utils.constants import JOBS_DEF_FILE, CORE_CLIENT_NAME, BROKER_ADDRESS
import paho.mqtt.client as mqtt
from pyplantie.utils.mylogger import new_logger
import json


logging.getLogger('apscheduler').setLevel(logging.WARNING)


class Core:

    scheduler = BlockingScheduler()

    def __init__(self):
        self.logger = new_logger(name=CORE_CLIENT_NAME, extra_handlers=['apscheduler'])

        self.client = mqtt.Client(CORE_CLIENT_NAME)
        self.client.connect(BROKER_ADDRESS)

        # self.scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        self.job_defs = {name: cls() for name, cls in inspect.getmembers(importlib.import_module(JOBS_DEF_FILE), inspect.isclass) if not name.startswith('_')}

        self.add_jobs()

    def start(self):
        self.scheduler.start()
        self.client.loop_forever()

    @staticmethod
    def job_func(client, job_info, logger):
        msg = json.dumps({"value": job_info.value})
        client.publish(
            topic=job_info.topic,
            payload=msg,
            qos=0,
        )
        logger.info(f'Event: {job_info.id}. Sent {msg} to topic {job_info.topic}')

    def add_jobs(self):

        for job_name, job_info in self.job_defs.items():
            job = self.scheduler.add_job(
                self.job_func,
                trigger=job_info.trigger,
                id=job_info.id,
                args=[self.client, job_info, self.logger],
                **job_info.trigger_args,
            )

            self.logger.info(f'Added {job_name} with id {job_info.id} and trigger {job.trigger}')


if __name__ == '__main__':
    app = Core()
    app.start()

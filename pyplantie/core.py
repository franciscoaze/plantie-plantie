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
from pyplantie.utils.constants import JOBS_DEF_FILE, CORE_CLIENT_NAME, BROKER_ADDRESS, DB_WATCHER_MIN
import paho.mqtt.client as mqtt
from pyplantie.utils.mylogger import new_logger
import json
from pyplantie.utils.sql_client import ElephantSQL
import pendulum

logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('SQL-CLIENT').setLevel(logging.DEBUG)


class Core:

    scheduler = BlockingScheduler()
    db_client = None

    def __init__(self):
        self.logger = new_logger(name=CORE_CLIENT_NAME, extra_handlers=['apscheduler','SQL-CLIENT'])

        self.client = mqtt.Client(CORE_CLIENT_NAME)
        self.client.connect(BROKER_ADDRESS)

        try:
            self.db_client = ElephantSQL()
            self.db_client.delete_table('Jobs')
            self.db_client.create_tables_if('Jobs')

        except Exception as exc:
            self.logger.warning(exc)

        self.job_defs = {name: cls() for name, cls in inspect.getmembers(importlib.import_module(JOBS_DEF_FILE), inspect.isclass) if not name.startswith('_')}

        self.add_jobs()

        watcher = self.scheduler.add_job(
            self.update_jobs_from_db,
            trigger="cron",
            id='db_watcher',
            args=[self, self.db_client, self.logger],
            minute=f'*/{DB_WATCHER_MIN}',
        )

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
            self.create_job_db(job_info)

    def create_job_db(self, job_info):
        self.db_client.update_table(
            table='Jobs',
            values={
                "name_id": job_info.id,
                "trigger_args": json.dumps(job_info.trigger_args),
                "value": job_info.value,
                "value_legend": job_info.value_legend
            }
        )

    @staticmethod
    def update_jobs_from_db(self, db_client, logger):
        """
        Makes a query to db every DB_WATCHER_MIN min to check if there are any changes in the jobs
        """
        results = db_client.get_data(
            table='JOBS',
            where_filter={"update_time >=": pendulum.now().subtract(minutes=DB_WATCHER_MIN).isoformat()})
        for res in results:
            name_id = res[1]
            trigger_args = json.loads(res[2])
            self.scheduler.reschedule_job(job_id=name_id, trigger='cron', **trigger_args)
            logger.info(f'Rescheduled job {name_id} for {trigger_args}')


if __name__ == '__main__':
    app = Core()
    app.start()
    app.update_jobs_from_db()
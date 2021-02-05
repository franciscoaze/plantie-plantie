import datetime
import psycopg2
import urllib.parse as up
from pyplantie.utils.constants import DATABASE_URL, TABLE_MODELS_FILE
from pyplantie.utils.mylogger import new_logger
import importlib
import inspect
import pendulum


class ElephantSQL:

    def __init__(self, database=DATABASE_URL, logger=None):
        if not logger:
            self.logger = new_logger(name='SQL-CLIENT', extra_handlers=['sql_debug'])
        else:
            self.logger = logger
        self.logger.debug(database)
        up.uses_netloc.append("postgres")
        url = up.urlparse(database)

        self.connection = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.connection.autocommit = True

        self.table_models = {name: cls for name, cls in inspect.getmembers(importlib.import_module(TABLE_MODELS_FILE), inspect.isclass) if not name.startswith('_')}

    def create_tables_if(self, table: str):
        table_model = self.table_models.get(table)
        if table_model:
            try:
                cursor = self.connection.cursor()
                create_new_query = f"CREATE TABLE IF NOT EXISTS {table_model.name} ({table_model.create_columns});"
                self.logger.debug(create_new_query)
                cursor.execute(create_new_query)
                self.connection.commit()
                cursor.close()
                self.logger.info(f'Successfully created table {table}')
                return True

            except Exception as error:
                # print("Error while connecting to PostgreSQL", error)
                self.logger.debug(error)
                return False

        else:
            self.logger.info(f'No model for {table}')
            return False

    def delete_table(self, table):
        table_model = self.table_models.get(table)
        if table_model:
            try:
                cursor = self.connection.cursor()
                create_new_query = f"DROP TABLE {table_model.name};"
                self.logger.debug(create_new_query)
                cursor.execute(create_new_query)
                self.connection.commit()
                cursor.close()
                self.logger.info(f'Successfully deleted table {table}')
                return True

            except Exception as error:
                # print("Error while connecting to PostgreSQL", error)
                self.logger.debug(error)
                return False

        else:
            self.logger.info(f'No model for {table}')
            return False

    def update_table(self, table: str, values: dict):
        table_model = self.table_models.get(table)
        if table_model:
            try:
                cursor = self.connection.cursor()
                postgres_insert_query = f"INSERT INTO {table_model.name}" \
                                        f" (update_time, {', '.join(list(values.keys()))})" \
                                        f" VALUES (%s, {', '.join(['%s' for val in list(values.keys())])});"""
                record_to_insert = (pendulum.now().isoformat(), *list(values.values()))

                self.logger.debug(postgres_insert_query)
                self.logger.debug(record_to_insert)

                cursor.execute(postgres_insert_query, record_to_insert)
                self.connection.commit()
                cursor.close()
                self.logger.info(f"Records were successfully inserted into {table}")
                return True
            except Exception as error:
                self.logger.warning(f"Error while connecting to PostgreSQL - {error}")
                return False
        else:
            self.logger.warning(f'No model for {table}')
            return False

    def get_data(self, table: str, where_filter: dict = None):
        where_query = ""
        query_values = ()
        if where_filter:
            where_query = f" where {'AND'.join([f'{key} %s' for key in where_filter.keys()])}"
            query_values = tuple(where_filter.values())

        select_query = f"select * from {table}{where_query};"
        self.logger.debug(select_query)
        self.logger.debug(query_values)

        try:
            cursor = self.connection.cursor()
            cursor.execute(select_query, query_values)

            results = cursor.fetchall()

            printed_results = "\n".join([str(res) for res in results])
            self.logger.debug(printed_results)
            cursor.close()
            return results

        except (Exception, psycopg2.Error) as error:
            self.logger.debug(error)
            return []


if __name__ == '__main__':
    try:
        cli = ElephantSQL()
        cli.delete_table('Jobs')
        cli.create_tables_if('Jobs')
        cli.update_table('Jobs', {"name_id": 'pump1', "trigger_args":"{'hour':1}", "value":3, "value_legend":"seconds"})

        cli.get_data('JOBS')
    finally:
        cli.connection.close()

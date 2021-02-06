
class Jobs(object):
    name = "JOBS"
    create_columns = "update_time TIMESTAMPTZ default current_timestamp, name_id text PRIMARY KEY, trigger_args text, value text, value_legend text, trigger text"
    columns = "update_time, name_id, trigger_args, value, value_legend, trigger"

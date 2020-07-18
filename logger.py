import os
import time
from database import insert_log
from configuration.vars import LOG_FILE

msg_dict = {True: "[DB]", False: ""}


def log_string(input_string, msg_type="SYSTEM INFO"):
    new_log = {"type": msg_type, "msg": input_string}
    success = insert_log(new_log)
    with open(LOG_FILE, 'a') as file:
        timestamp = time.asctime()
        file.write(f'{timestamp} {msg_dict[success]}: {input_string}\n')


if __name__ == '__main__':
    log_string('Alive')
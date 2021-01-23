#!/bin/bash
projects_dir="/home/pi/Desktop/Projects"
sudo service mosquitto stop
mosquitto &
lxterminal --command="bash -c 'source $projects_dir/.venv/bin/activate; cd plantie-plantie; python -m pyplantie.arduino_rwi; bash'" &
lxterminal --command="bash -c 'source $projects_dir/.venv/bin/activate; cd plantie-plantie; python -m pyplantie.raspberry_rwi; bash'" &

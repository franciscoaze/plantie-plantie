#!/bin/bash
sudo service mosquitto stop
mosquitto
lxterminal --command="bash -c 'source .venv/bin/activate; cd plantie-plantie; python -m pyplantie.arduino_rwi; bash'"
lxterminal --command="bash -c 'source .venv/bin/activate; cd plantie-plantie; python -m pyplantie.raspberry_rwi; bash'"
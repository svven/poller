#!/bin/bash

## Run poller/dispatcher.py

echo 'Start dispatcher'

## Activate the virtualenv
. env/bin/activate

python -c "from poller import dispatcher; dispatcher.dispatch()"

echo 'End dispatcher'

## Deactivate the virtualenv
deactivate
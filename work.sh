#!/bin/bash

## Fake rqworker running summarizer/worker.py
## If you want to run it directly, just `PATH = .:PATH` before

echo 'Start worker'

## Can be run w/o an active virtualenv as it activates it here
. env/bin/activate

## Pass in the command line args just like the regular rqworker
python -c 'from poller import worker' $@

# ## Real rqworker
# if [ $@ ]; then
# 	rqworker $@
# else
# 	rqworker -c poller.config
# fi

echo 'End worker'

## Deactivate the virtualenv
deactivate
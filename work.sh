#!/bin/bash

## Real rqworker

echo 'Start worker'

## Can be run w/o an active virtualenv as it activates it here
. env/bin/activate

if [ $@ ]; then
	rqworker $@
else
	rqworker -c poller.config
fi

echo 'End worker'

## Deactivate the virtualenv
deactivate
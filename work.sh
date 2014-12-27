#!/bin/bash

## Real rqworker

echo 'Start worker'

## Can be run w/o an active virtualenv as it activates it here
. env/bin/activate

rqworker poller

echo 'End worker'

## Deactivate the virtualenv
deactivate
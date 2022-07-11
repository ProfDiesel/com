#!/usr/bin/env python
from logging import getLogger
from logging.config import dictConfig
from json import load
from time import sleep

LOGGER = getLogger('pipo')

dictConfig(load(open('../resources/logging.json')))
LOGGER.error('pipololo')
sleep(5)


import logging
import sys
import typing

__author__ = 'peter.amstutz@curoverse.com'

_logger = logging.getLogger("salad")
_logger.addHandler(logging.StreamHandler())
_logger.setLevel(logging.INFO)

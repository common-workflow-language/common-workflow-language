import logging
import sys
if sys.version_info >= (2,7):
    import typing

__author__ = 'peter.amstutz@curoverse.com'

_logger = logging.getLogger("salad")
_logger.addHandler(logging.StreamHandler())
_logger.setLevel(logging.INFO)

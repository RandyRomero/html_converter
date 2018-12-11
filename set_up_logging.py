# -*- coding: utf-8 -*-

import logging


def get_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s module %(name)s >> lineno %(lineno)d << %(message)s - %(asctime)s  ')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
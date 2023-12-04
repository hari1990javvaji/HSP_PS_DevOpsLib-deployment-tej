"""
Module to log error/info in a file
"""
import logging
import textwrap


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='./deploy.log',
    filemode='a'
)


def log(msg):
    """
    Simple function to print log messages
    :param msg:
    :param log_type:
    :return:
    """
    print(msg)
    logging.info(msg)

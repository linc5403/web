import logging
from io import StringIO
# import socket
import sys
import traceback


logger = logging.getLogger()

# from download.settings import LOGGING

# unexcepted_logger = logging.getLogger()
# # unexcepted_logger = logging.getLogger('track_back')
# handler = logging.handlers.SysLogHandler(
#     address=('172.16.11.4', 514),
#     socktype=socket.SOCK_DGRAM,
# )
# formatter = logging.Formatter(LOGGING['formatters']['verbose']['format'])
# handler.setFormatter(formatter)
# unexcepted_logger.addHandler(handler)
# unexcepted_logger.setLevel(logging.DEBUG)


def log_trace_back(exctype, value, tb):
    log_file = StringIO()
    traceback.print_exception(exctype, value, tb, file=log_file)
    logger.error('{}'.format(log_file.getvalue()))

    # unexcepted_logger.error('{}'.format(log_file.getvalue()))
    # unexcepted_logger.error('{} {} {}'.format(
    #     exctype, value, repr(tb)
    # ))


sys.excepthook = log_trace_back

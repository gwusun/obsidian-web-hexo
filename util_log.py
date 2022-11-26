# 创建logger对象
import logging
import os.path
import sys


class ConstHandler:
    FILE_HANDLER = "FileHandler"
    STREAM_HANDLER = "FileHandler"
    MYSQL_HANDLER = "FileHandler"


logger = logging.getLogger("log_utils")
logger.setLevel(logging.INFO)


def get_console_handler():
    return get_stream_handler()


def get_stream_handler():
    # stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.set_name(ConstHandler.STREAM_HANDLER)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s '))
    return stream_handler


def get_mysql_handler():
    from pysearchlib.logging.MysqlLogHandler import MysqlLogHandler
    # 设置日志配置
    formatter = logging.Formatter('%(asctime)s - %(user)s - %(levelname)s %(message)s')
    # 写日志到数据库中
    dblog = MysqlLogHandler(
        uri="mysql+pymysql://root:qwerasdf1234@114.55.41.175:9201/nni_experiments?charset=utf8"
    )
    dblog.set_name(ConstHandler.MYSQL_HANDLER)
    dblog.setFormatter(formatter)
    return dblog


def get_file_handler():
    # 追加写入文件a ，设置utf-8编码防止中文写入乱码

    file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "debug.log"), 'a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(filename)s - line:%(lineno)d -%(process)s - %(levelname)s - %('
                          'message)s '))
    file_handler.set_name(ConstHandler.FILE_HANDLER)
    return file_handler


def is_existed_hander(hander_name):
    existed_handlers = [h.name for h in logger.handlers]
    return hander_name in existed_handlers


def get_console_logger(level=logging.DEBUG):
    if not is_existed_hander(ConstHandler.STREAM_HANDLER):
        stream_handler = get_stream_handler()
        logger.addHandler(stream_handler)
    return logger


def get_file_logger(level=logging.DEBUG):
    if not is_existed_hander(ConstHandler.FILE_HANDLER):
        file_handler = get_file_handler()
        # 加载文件到logger对象中
        logger.addHandler(file_handler)
    return logger


def get_file_and_console_logger(level=logging.DEBUG):
    # 加载文件到logger对象中
    if not is_existed_hander(ConstHandler.FILE_HANDLER):
        logger.addHandler(get_file_handler())
    if not is_existed_hander(ConstHandler.STREAM_HANDLER):
        logger.addHandler(get_stream_handler())
    return logger


def get_mysql_logger(level=logging.DEBUG):
    if not is_existed_hander(ConstHandler.MYSQL_HANDLER):
        dblog = get_mysql_handler()
        logger.addHandler(dblog)
    return logger


def get_logger():
    return get_console_logger()


def log_heading(log: logging.Logger, message=""):
    log.info(f"\n============={message}===============\n")

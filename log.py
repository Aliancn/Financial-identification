import logging
import time


class SimpleLogger:
    _instance = None

    def __new__(cls, log_level=logging.INFO):
        if cls._instance is None:
            cls._instance = super(SimpleLogger, cls).__new__(cls)
            cls._instance.__init__(log_level=log_level)
        return cls._instance

    def __init__(self, log_file='./log/app.log', log_level=logging.INFO):
        log_file = time.strftime('%Y-%m-%d', time.localtime())
        log_file = f'./log/{log_file}.log'

        self.logger = logging.getLogger('SimpleLogger')
        self.logger.setLevel(log_level)

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # 创建格式化器并将其添加到处理器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 将处理器添加到记录器
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


logger = SimpleLogger(log_level=logging.DEBUG)

import logging
import os

class SimpleLogger:
    def __init__(self, log_file='app.log', log_level=logging.INFO):
        self.logger = logging.getLogger('SimpleLogger')
        self.logger.setLevel(log_level)

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # 创建格式化器并将其添加到处理器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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


logger = SimpleLogger(log_file='app.log', log_level=logging.DEBUG)

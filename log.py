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
# 示例用法
# if __name__ == "__main__":
#     logger = SimpleLogger(log_file='app.log', log_level=logging.DEBUG)
#     logger.debug('这是一个调试消息')
#     logger.info('这是一个信息消息')
#     logger.warning('这是一个警告消息')
#     logger.error('这是一个错误消息')
#     logger.critical('这是一个严重错误消息')
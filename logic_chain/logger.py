import logging

class Logger:
    def __init__(self, 
                 log_file_path,
                 level = logging.INFO):
        logger = logging.getLogger()
        handler = logging.FileHandler(log_file_path, encoding="utf-8")
        formatter = logging.Formatter(
                '%(asctime)s - %(levelname)-8s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        self.logger = logger
    
    def error(self, message, error_message):
        self.logger.error(message)
        self.logger.error(f"error details is: {error_message}")
    
    def info(self, message):
        self.logger.info(message)
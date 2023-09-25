import logging

class Logger:

    def __init__(self, logname, loglevel=logging.DEBUG):
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(loglevel)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add console handler
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger

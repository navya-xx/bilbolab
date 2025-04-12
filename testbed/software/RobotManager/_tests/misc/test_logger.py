from core.utils.logging_utils import Logger, enable_redirection, setLoggerLevel


def log_redirect_function(log_entry, log, logger, level):
    print(log_entry)


if __name__ == '__main__':
    logger = Logger('TEST 1', level='INFO')
    logger2 = Logger('TEST 2')
    setLoggerLevel('TEST 2', 'WARNING')
    enable_redirection(log_redirect_function, redirect_all=True)
    logger.info('test1')
    logger2.warning('test2')
    logger2.info('test3')

import logging
import colorlog

# 定义一个全局变量logger，用于存储单例的logger对象
logger = None

def newLogger():
    # 使用global关键字来声明logger变量是全局变量，而不是局部变量
    global logger
    # 如果logger变量为None，说明还没有创建过logger对象，就创建一个新的对象
    if logger is None:
        # 创建一个logger对象
        logger = logging.getLogger("Manayana")
        # 设置日志级别为DEBUG，这样可以输出所有级别的日志
        logger.setLevel(logging.DEBUG)
        # 创建一个StreamHandler对象，用于输出日志到控制台
        console_handler = logging.StreamHandler()
        # 设置控制台输出的日志格式和颜色
        logger.propagate = False
        console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        console_colors = {
            'DEBUG': 'white',
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
        console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
        console_handler.setFormatter(console_formatter)
        # 将控制台处理器添加到logger对象中
        logger.addHandler(console_handler)
    # 如果logger变量不为None，说明已经创建过logger对象，就不需要再创建新的对象，直接返回已有的对象
    else:
        return logger
    # 创建一个FileHandler对象，用于输出日志到文件
    file_handler = logging.FileHandler('log.txt', mode='w')
    # 设置文件输出的日志格式
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_formatter = logging.Formatter(file_format)
    file_handler.setFormatter(file_formatter)
    # 将文件处理器添加到logger对象中
    logger.addHandler(file_handler)
    return logger
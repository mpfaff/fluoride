from aenum import OrderedEnum, NoAlias
from enum import Enum

class Style(Enum):
    BLACK = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    ORANGE = '\033[38;2;191;131;97m'
    DIAMOND = '\033[38;2;179;227;226m'

    FATAL = RED
    STDERR = RED
    ERROR = ORANGE
    SUCCESS = GREEN
    STDOUT = BLUE
    WARNING = YELLOW
    INFO = BLUE
    FINE = BLUE
    FINER = BLUE
    FINEST = BLUE
    
    LOGGER_NAME = MAGENTA
    # DEPRECATED: Prefer Style.TAG
    TIME = DIAMOND
    TAG = DIAMOND

    @staticmethod
    def bold(msg):
        return '\033[1m' + str(msg) + '\033[22m'

    @staticmethod
    def italic(msg):
        return '\033[3m' + str(msg) + '\033[23m'
    
    @staticmethod
    def underline(msg):
        return '\033[4m' + str(msg) + '\033[24m'

    def format(self, msg):
        return self.value + str(msg) + '\033[39m'


class Level(OrderedEnum, init='level color', settings=NoAlias):
    __ordered__ = 'FATAL STDERR ERROR SUCCESS STDOUT PRINT WARNING INFO FINE FINER FINEST'

    FATAL = 50, Style.FATAL
    STDERR = 45, Style.STDERR
    ERROR = 40, Style.ERROR
    #ERROR = 40, '\033[38;2;179;227;226m'
    SUCCESS = 36, Style.SUCCESS
    STDOUT = 35, Style.STDOUT
    WARNING = 30, Style.WARNING
    INFO = 20, Style.INFO
    FINE = 15, Style.FINE
    FINER = 10, Style.FINER
    FINEST = 5, Style.FINEST
    
    def format(self, msg):
        return self.color.format(str(msg))
    
    def formatName(self):
        return self.format(self.name)
    
    def __eq__(self, other):
        if type(other) is Level:
            return self.value == other.value
        if type(other) is int:
            return self.value == other
        return NotImplemented
    
    def __ne__(self, other):
        if type(other) is Level:
            return self.value != other.value
        if type(other) is int:
            return self.value != other
        return NotImplemented
    
    def __gt__(self, other):
        if type(other) is Level:
            return self.value > other.value
        if type(other) is int:
            return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        if type(other) is Level:
            return self.value >= other.value
        if type(other) is int:
            return self.value >= other
        return NotImplemented
    
    def __lt__(self, other):
        if type(other) is Level:
            return self.value < other.value
        if type(other) is int:
            return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        if type(other) is Level:
            return self.value <= other.value
        if type(other) is int:
            return self.value <= other
        return NotImplemented
    
    def format(self, msg):
        return self.color.format(str(msg))
    
    def formatName(self):
        return self.format(self.name)

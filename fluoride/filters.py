from logging import Filter, LogRecord

from fluoride.core import Level

class NoErrorFilter(Filter):
    def filter(self, record: LogRecord):
        lvl = Level[record.levelname]
        return lvl < Level.ERROR and lvl != Level.WARNING

class JustErrorFilter(Filter):
    def filter(self, record: LogRecord):
        lvl = Level[record.levelname]
        return lvl >= Level.ERROR or lvl == Level.WARNING

class NoEmptyFilter(Filter):
    def filter(self, record: LogRecord):
        return record.msg.strip().strip('\n') != ''

from collections import namedtuple
import datetime as dt
import inspect
import io
from logdna import LogDNAHandler
import logging
import logging.handlers
import os
from pathlib import Path
import platform
import re
import socket
from string import Template
import sys
import syslog
from types import TracebackType

from fluoride.core import Level, Style
import fluoride.filters as filters
from fluoride.util import ensure_dir

sys_stdout = sys.stdout
sys_stderr = sys.stderr

ExcInfo = namedtuple('ExcInfo', ['exc_type', 'value', 'traceback'])

class Formatter(logging.Formatter):
    multiline_fmt = Template(' | $message')

    def __init__(self, fmt: Template):
        """
        Initialize the formatter with specified format strings.

        Initialize the formatter either with the specified format string, or a
        default as described above. Allow for specialized date formatting with
        the optional datefmt argument. The $isotime fmt argument gets you get an
        ISO8601-like format.

        .. versionchanged:: 3.2
           Added the ``style`` parameter.
        """
        self.fmt = fmt
    
    def formatTime(self, time):
        """
        Return the creation time of the specified LogRecord as formatted text.

        This method should be called from format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        in formatters to provide for any specific requirement, but the
        basic behaviour is as follows: if datefmt (a string) is specified,
        it is used with time.strftime() to format the creation time of the
        record. An ISO8601-like format is used.
        The resulting string is returned. This function uses a user-configurable
        function to convert the creation time to a tuple. By default,
        time.localtime() is used; to change this for a particular formatter
        instance, set the 'converter' attribute to a function with the same
        signature as time.localtime() or time.gmtime(). To change it for all
        formatters, for example if you want all logging times to be shown in GMT,
        set the 'converter' attribute in the Formatter class.
        """
        return dt.datetime.fromtimestamp(time).isoformat(timespec='milliseconds')

    def format(self, record: logging.LogRecord):
        """
        Format the specified record as text.

        The record's attribute dictionary is used as the operand to a
        string formatting operation which yields the returned string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record is computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() is
        called to format the event time. If there is exception information,
        it is formatted using formatException() and appended to the message.
        """
        record.message = record.getMessage()
        record.asctime = self.formatTime(record.created)
        if '\n' in record.message.rstrip('\n'):
            splitted = record.message.strip('\n').splitlines()
            s = self.fmt.substitute({
                'isotime': Style.TAG.format(record.asctime),
                'levelname': Level[record.levelname].formatName(),
                'name': Style.LOGGER_NAME.format(record.name),
                'module': Style.TAG.format(record.module),
                'lineno': Style.TAG.format(str(record.lineno)),
                'message': Level[record.levelname].color.format(splitted.pop(0) + '\n' + '\n'.join(self.multiline_fmt.substitute(message=line) for line in splitted)),
            })
        else:
            s = self.fmt.substitute({
                'isotime': Style.TAG.format(record.asctime),
                'levelname': Level[record.levelname].formatName(),
                'name': Style.LOGGER_NAME.format(record.name),
                'module': Style.TAG.format(record.module),
                'lineno': Style.TAG.format(str(record.lineno)),
                'message': Level[record.levelname].format(record.message),
            })

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s

for level in Level:
    logging.addLevelName(level.level, level.name)


class StreamToLogger(object):
    """
    Fake file-like stream object that blocks messages matching `self.filter`, redirecting all other output writes to `self.logger`.
    """
    def __init__(self, logger, log_level: Level, linked_stream, filt = None):
        self.logger = logger
        self.log_level = log_level
        self.filter = filt
        self.linked_stream = linked_stream

    def write(self, buf, *args, **kwargs):
        if type(buf) is bytes:
            self.linked_stream.write(buf.decode())
        else:
            filt_none = self.filter is None
            if filt_none or (not filt_none and not self.filter.search(buf)):
                self.logger._log(self.log_level.level, buf, args, **kwargs)
    
    def isatty(self):
        """Returns the result of `self.linked_stream.isatty()`"""
        return self.linked_stream.isatty()
    
    def flush(self):
        """Returns the result of `self.linked_stream.flush()`"""
        return self.linked_stream.flush()

class NullStream(object):
    """
    Fake file-like stream object that ignores all messages.
    """
    def __init__(self):
        pass

    def write(self, buf, *args, **kwargs):
        pass
    
    def isatty(self):
        """Returns True"""
        return True
    
    def flush(self):
        pass


def _gen_error_handler():
    handler: logging.StreamHandler = logging.StreamHandler(sys_stderr)
    handler.setFormatter(Formatter(Template('[$isotime]: [$levelname]: [$name]: [$module:$lineno]: $message')))
    handler.setLevel(Level.WARNING.level)
    handler.addFilter(filters.JustErrorFilter())
    handler.addFilter(filters.NoEmptyFilter())
    return handler

class App():
    def __init__(self, name: str, console_log: bool = True, dna_log: bool = False, stream_log: bool = False, sys_log: bool = False, dna_token: str = None, stream_file_path: str = None):
        self.name = name
        self.console_log = console_log
        self.dna_log = dna_log
        self.stream_log = stream_log
        self.sys_log = sys_log
        self.dna_token = dna_token

        #
        # ROOT LOGGING INITIALIZATION STAGE
        #

        #self.root_handler: logging.StreamHandler = 

        if self.console_log:
            self.error_handler: logging.StreamHandler = _gen_error_handler()
            self.root_handler: logging.StreamHandler = self.error_handler
            self.root_handler: logging.StreamHandler = logging.StreamHandler(NullStream())
        else:
            self.root_handler: logging.StreamHandler = logging.StreamHandler(NullStream())

        logging.basicConfig(
            level=Level.WARNING.level,
            handlers=[
                self.root_handler
            ]
        )

        #
        # APP LOGGING INITIALIZATION STAGE
        #

        self.logger: logging.Logger = logging.getLogger(self.name)

        if self.dna_log:
            self.dna_handler: LogDNAHandler = LogDNAHandler(
                dna_token,
                {
                    'app': self.name,
                    'include_standard_meta': True,
                    'hostname': socket.gethostname(),
                    'index_meta': True
                }
            )
            self.logger.addHandler(self.dna_handler)

        if self.sys_log:
            if os.name == 'posix':
                _address = ('localhost', 514)

                self.sys_handler: logging.handlers.SysLogHandler = logging.handlers.SysLogHandler(address=_address, facility=syslog.LOG_LOCAL1)
                self.sys_handler.ident = self.name.replace(' ', '_')
                self.sys_handler.setLevel(Level.FINEST.level)
                self.logger.addHandler(self.sys_handler)

        if self.stream_log:
            if platform.system() == 'Darwin':
                directory = f'{Path.home()}/Library/Logs'
                ensure_dir(directory)
                self.stream_handler: logging.FileHandler = logging.FileHandler(f'{directory}/{self.name.lower().replace(" ", "-")}.log')
                self.stream_handler.setLevel(Level.FINEST.level)
            else:
                ensure_dir('log')
                self.stream_handler: logging.FileHandler = logging.FileHandler(f'log/{self.name.lower().replace(" ", "-")}.log')
                self.stream_handler.setLevel(Level.FINEST.level)

            self.logger.addHandler(self.stream_handler)

        if self.console_log:
            self.console_handler: logging.StreamHandler = logging.StreamHandler(sys_stdout)
            self.console_handler.setFormatter(Formatter(Template('[$isotime]: [$levelname]: [$name]: [$module:$lineno]: $message')))
            self.console_handler.setLevel(Level.FINE.level)
            self.console_handler.addFilter(filters.NoErrorFilter())
            self.console_handler.addFilter(filters.NoEmptyFilter())
            self.logger.addHandler(self.console_handler)

            #self.error_handler: logging.StreamHandler = _gen_error_handler()
            self.logger.addHandler(self.error_handler)


        if type(sys.stdout) is not StreamToLogger:
            self.stdout: StreamToLogger = StreamToLogger(None, Level.STDOUT, sys_stdout)
            self.stdout.logger = self.logger
            sys.stdout = self.stdout
        if type(sys.stderr) is not StreamToLogger:
            self.stderr: StreamToLogger = StreamToLogger(None, Level.STDERR, sys_stderr, re.compile('[A-Z]+:[^:]+:.*'))
            self.stderr.logger = self.logger
            sys.stderr = self.stderr

        # TODO: Figure out why this was creating an infinite loop.
        #self.excepthook = log_exc_sys(exc_type, value, tb)
        #sys.excepthook = self.excepthook
    
    def log(self, level: Level, msg, *args, **kwargs):
        self.logger._log(level.level, msg, args, **kwargs)
    
    def log_exc_bundle(self, exc_info: ExcInfo, level: Level = Level.ERROR):
        """Logs stacktrace and exception information.

        Parameters:
            exc_info (tuple): If given, should be a tuple in the format `(exc_type, value, traceback)` as used by `sys.excepthook` and `Logger#error` and as returned by `sys.exc_info()`
            level (Level): If specified, the level the exception will be logged at.
        """

        value_status = exc_info[1] is not None and str(exc_info[1]).replace(' ', '').replace('\n', '') != ''
        self.logger._log(level, f'{exc_info[0].__name__}: {exc_info[1] if value_status else "No message"}', exc_info=exc_info)

    def log_exc_sys(exc_type: type = None, value = None, tb: TracebackType = None, level: Level = Level.ERROR):
        """Logs stacktrace and exception information relevant to tb.

        Of exc_type, value and tb, any values of None will be filled in from sys.exc_info() and other methods.

        Parameters:
            exc_type (type): The type of the exception
            value: Contains a short message about the exception
            tb (TracebackType): The traceback from the exception
            level (core.Level): The level the exception should be logged at. Defaults to `core.level.Error`
        """
        exc_info = sys.exc_info()

        if exc_type is None:
            exc_type = exc_info[0]

        if value is None:
            value = exc_info[1]
        
        if tb is None:
            tb = exc_info[2]
        
        value_status = value is not None and str(value).replace(' ', '').replace('\n', '') != ''

        out = f'{exc_type.__name__}{": " + str(value) if value_status else ""}\nTraceback (most recent call last):'
        # For future reference, the internal name of `lines` is `code_context`
        # All others use internal name
        for frame, filename, lineno, function, lines, index in reversed(inspect.stack()[2:]):
            if 'vscode' not in filename and 'runpy.py' not in filename:
                out += f'\n  File "{filename}", line {lineno}, in {function}'
                for line in lines:
                    out += f'\n    `{line.strip()}`'
        for frame, filename, lineno, function, lines, index in inspect.getinnerframes(tb):
            if 'vscode' not in filename and 'runpy.py' not in filename:
                out += f'\n  File "{filename}", line {lineno}, in {function}'
                for line in lines:
                    out += f'\n    `{line.strip()}`'
        
        out += f'\n{exc_type.__name__}{": " + str(value) if value_status else ""}'
        
        self.logger._log(level, out)

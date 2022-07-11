from logging import Handler, LogRecord
from logging import Handler, LogRecord
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from json import dumps
from logging import Formatter, LogRecord
from traceback import format_exception
from typing import Any, Collection
from functools import partial


_HAS_ALERTA = True
try:
    from alertaclient.api import Client
    from alertaclient.auth.utils import get_token
    from alertaclient.config import Config
except ImportError:
    _HAS_ALERTA = False


_HAS_RICH = True
try:
    from rich.logging import RichHandler
    from rich.console import Console
except ImportError:
    _HAS_RICH = False


class JsonFormatter(Formatter):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def format(self, record: LogRecord) -> str:
        record_dict = {'ts': super().formatTime(record), 'lvl': record.levelname, 'msg': record.getMessage(), **record.args}
        if record.exc_info:
            record_dict['exc'] = format_exception(record.exc_info)
        return dumps(record_dict)


class AsyncHandler(Handler):
    def __init__(self, upstream_handlers: Collection[Handler], start: bool = True):
        super().__init__()
        queue = Queue()
        self.__handler = QueueHandler(queue)
        print(upstream_handlers)
        self.__listener = QueueListener(queue, *upstream_handlers)
        if start:
            self.__listener.start()
        print('__init__')

    def __del__(self):
        self.__listener.stop()
        print('__del__')

    def emit(self, record: LogRecord):
        self.__handler.emit(record)
        print('emit')


if _HAS_ALERTA:
    class AlertaHandler(Handler):
        def __init__(self, resource: str = '', event: str = '', **kwargs) -> None:
            self.__resource = resource
            self.__event = event
            config = Config()
            config.options.update(**kwargs)
            self.__client = Client(
                endpoint=config.options['endpoint'],
                key=config.options['key'],
                secret=config.options['secret'],
                token=get_token(config.options['endpoint']),
                username=config.options.get('username', None),
                password=config.options.get('password', None),
                timeout=float(config.options['timeout']),
                ssl_verify=config.options['sslverify'],
                ssl_cert=config.options.get('sslcert', None),
                ssl_key=config.options.get('sslkey', None),
                debug=config.options['debug']
            )

        def emit(self, record: LogRecord) -> None:
            kwargs = dict(resource=self.__resource, event=self.__event, text=super().format(record)) | getattr(record, 'alerta_args', {})
            try:
                id, alert, message = self.__client.send_alert(resource=resource, event=event, text=text, **kwargs)
            except:
                FALLBACK_LOGGER.exception()


if _HAS_RICH:
    class ConsoleHandler(RichHandler):
        def __init__(self, *args, **kwargs):
            print('console')
            super().__init__(console=Console(stderr=True), *args, **kwargs)


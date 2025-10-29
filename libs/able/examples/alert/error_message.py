import os
import traceback

from kivy.base import (
    ExceptionHandler,
    ExceptionManager,
    stopTouchApp,
)
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.logger import Logger


Builder.load_file(os.path.join(os.path.dirname(__file__), 'error_message.kv'))


class ErrorMessageOnException(ExceptionHandler):

    def handle_exception(self, exception):
        Logger.exception('Unhandled Exception catched')
        message = ErrorMessage(message=traceback.format_exc())

        def raise_exception(*ar2gs, **kwargs):
            stopTouchApp()
            raise Exception("Exit due to errors")

        message.bind(on_dismiss=raise_exception)
        message.open()
        return ExceptionManager.PASS


class ErrorMessage(Popup):
    title = StringProperty('Bang!')
    message = StringProperty('')


def install_exception_handler():
    ExceptionManager.add_handler(ErrorMessageOnException())

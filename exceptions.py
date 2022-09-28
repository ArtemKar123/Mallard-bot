import enum


class ProcessingException(Exception):
    class ProcessingExceptionType(enum.Enum):
        none = 0
        file_too_large = 1
        unexpected = 2
        wrong_source_type = 3
        arguments_parsing_error = 4

    __ERROR_MESSAGES = {
        ProcessingExceptionType.none: '',
        ProcessingExceptionType.file_too_large: 'Файл слишком большой :(',
        ProcessingExceptionType.unexpected: 'Что-то сломалось :(',
        ProcessingExceptionType.wrong_source_type: 'Я такое квотить не умею :(',
        ProcessingExceptionType.arguments_parsing_error: ''
    }

    def __init__(self, exception_type: ProcessingExceptionType = ProcessingExceptionType.none,
                 additional_message: str = ''):
        self.__message = self.__ERROR_MESSAGES[exception_type] + additional_message

    def __str__(self):
        return 'Не ква!\n' + self.__message

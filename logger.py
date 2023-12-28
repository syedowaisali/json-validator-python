
from formatter import format_output


class AppLogger:

    def __init__(self):
        self.error_set = set()
        self.warn_set = set()
        self.success_set = set()
        self.info_set = set()

    def warn(self, message, line_separator=False):
        formatted_message = format_output(f"(yellow)WARN   ::(end)  {message}")
        self.__log(formatted_message, self.warn_set, line_separator)

    def error(self, message, line_separator=False):
        formatted_message = format_output(f"(red)ERROR  ::(end)  {message}")
        self.__log(formatted_message, self.error_set, line_separator)

    def success(self, message, line_separator=False):
        formatted_message = format_output(f"(green)SUCCESS ::(end)  {message}")
        self.__log(formatted_message, self.success_set, line_separator)

    def info(self, message, line_separator=False):
        formatted_message = format_output(f"(blue)INFO   ::(end)  {message}")
        self.__log(formatted_message, self.info_set, line_separator)

    def line_separator(self):
        print("-" * 100)

    def has_no_error(self):
        return len(self.error_set) == 0

    def __log(self, message, log_set: set, line_separator=False):
        prev_count = len(log_set)
        log_set.add(message)
        if prev_count != len(log_set):
            print(message)
            if line_separator:
                self.line_separator()


logger = AppLogger()

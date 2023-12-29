from config import configs, enable_output_tags, formatted_output



class AppLogger:

    def __init__(self):
        self.error_set = set()
        self.warn_set = set()
        self.success_set = set()
        self.info_set = set()

    def warn(self, message, line_separator=False):
        output = self.get_output("(yellow)WARN    ::(end)  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.warn_set, line_separator)

    def error(self, message, line_separator=False):
        output = self.get_output("(red)ERROR   ::(end)  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.error_set, line_separator)

    def success(self, message, line_separator=False):
        output = self.get_output("(green)SUCCESS ::(end)  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.success_set, line_separator)

    def info(self, message, line_separator=False):
        output = self.get_output("(blue)INFO    ::(end)  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.info_set, line_separator)

    def get_output(self, tag: str, message: str) -> str:
        output = tag if configs.get(enable_output_tags) else ""
        return f"{output}{message}"

    def apply_formatting(self, output: str) -> str:
        return self.format_output(output) if configs.get(formatted_output) else self.remove_formatting(output)

    def line_separator(self):
        if configs.get(formatted_output):
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

    def format_output(self, text: str) -> str:
        return (text
                .replace('(bold)', "\033[1m")
                .replace("(red)", "\033[31m")
                .replace("(green)", "\033[32m")
                .replace("(blue)", "\033[34m")
                .replace("(yellow)", "\033[33m")
                .replace("(end)", "\033[0m")
                )

    def remove_formatting(self, text: str) -> str:
        return (text
                .replace('(bold)', "")
                .replace("(red)", "")
                .replace("(green)", "")
                .replace("(blue)", "")
                .replace("(yellow)", "")
                .replace("(end)", "")
                )


logger = AppLogger()

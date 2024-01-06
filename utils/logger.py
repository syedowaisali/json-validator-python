from config import configs, enable_output_tags, formatted_output



class AppLogger:

    def __init__(self):
        self.error_set = set()
        self.warn_set = set()
        self.success_set = set()
        self.info_set = set()
        self.all_error_list = []
        self.all_warn_list = []
        self.all_info_list = []
        self.all_success_list = []

    def warn(self, message, line_separator=False):
        output = self.get_output("(yellow)", "WARN    ::  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.warn_set, message, line_separator)

    def error(self, message, line_separator=False):
        output = self.get_output("(red)", "ERROR   ::  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.error_set, message, line_separator)

    def success(self, message, line_separator=False):
        output = self.get_output("(green)", "SUCCESS ::  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.success_set, message, line_separator)

    def info(self, message, line_separator=False):
        output = self.get_output("(blue)", "INFO    ::  ", message)
        formatted_message = self.apply_formatting(output)
        self.__log(formatted_message, self.info_set, message, line_separator)

    def get_output(self, color, tag: str, message: str) -> str:
        output = tag if configs.get(enable_output_tags) else ""
        end = "(end)" if configs.get(enable_output_tags) else ""
        return f"{color}{output}{message}{end}"

    def apply_formatting(self, output: str) -> str:
        return self.__format_output(output) if configs.get(formatted_output) else self.__remove_formatting(output)

    def line_separator(self):
        if configs.get(formatted_output):
            pass #print("" * 100)

    def has_no_error(self):
        return len(self.error_set) == 0

    def finalize(self):
        #print("*=" * 100)

        self.all_error_list.extend(self.error_set)
        self.all_warn_list.extend(self.warn_set)
        self.all_info_list.extend(self.info_set)
        self.all_success_list.extend(self.success_set)

        self.error_set.clear()
        self.warn_set.clear()
        self.info_set.clear()
        self.success_set.clear()

    def __log(self, formatted_message, log_set: set, message, line_separator=False):

        print(formatted_message)
        #prev_count = len(log_set)
        #log_set.add(message)
        #if prev_count != len(log_set):
         #   print(formatted_message)
          #  if line_separator:
           #     self.line_separator()

    def __format_output(self, text: str) -> str:
        return (text
                .replace('(bold)', "\033[1m")
                .replace("(black)", "\033[30m")
                .replace("(red)", "\033[31m")
                .replace("(green)", "\033[32m")
                .replace("(blue)", "\033[34m")
                .replace("(yellow)", "\033[33m")
                .replace("(end)", "\033[0m")
                )

    def __remove_formatting(self, text: str) -> str:
        return (text
                .replace('(bold)', "")
                .replace("(black)", "")
                .replace("(red)", "")
                .replace("(green)", "")
                .replace("(blue)", "")
                .replace("(yellow)", "")
                .replace("(end)", "")
                )


logger = AppLogger()

from config import root_object_path


def format_output(text: str) -> str:
    return (text
            .replace('(bold)', "\033[1m")
            .replace("(red)", "\033[31m")
            .replace("(green)", "\033[32m")
            .replace("(blue)", "\033[34m")
            .replace("(yellow)", "\033[33m")
            .replace("(end)", "\033[0m")
            )


def normalize_path(path: str) -> str:
    path = path.replace(root_object_path, "") if len(path) > len(root_object_path) else path
    return path[1:] if path.startswith(".") else path

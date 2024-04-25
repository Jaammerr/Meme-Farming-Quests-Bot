class MemeError(Exception):
    def __init__(self, error_dict: dict):
        self.error_dict = error_dict

    def error_message(self) -> str:
        return self.error_dict.get("error_message")

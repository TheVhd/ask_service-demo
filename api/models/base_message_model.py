class BaseMessage:
    def __init__(self, type: str, role: str, content: str):
        self.type = type
        self.role = role
        self.content = content

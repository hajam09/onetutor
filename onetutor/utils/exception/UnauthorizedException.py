class UnauthorizedException(Exception):

    def __init__(self):
        super().__init__("User not authorized for this operation")

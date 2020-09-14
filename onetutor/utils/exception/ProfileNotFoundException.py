class ProfileNotFoundException(Exception):

    def __init__(self, user):
        super().__init__(f"No profile found for user with email: {user.email}")

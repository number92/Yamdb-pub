from reviews.validators import validate_username


class ValidateUsernameMixin:
    def validate_username(self, value):
        return validate_username(value)

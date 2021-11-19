def isPasswordStrong(password):
    if len(password) < 8:
        return False

    if not any(letter.isalpha() for letter in password):
        return False

    if any(capital.isupper() for capital in password):
        return False

    if any(number.isdigit() for number in password):
        return False

    return True

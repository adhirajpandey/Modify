def input_validation(username, password):
    MIN_LENGTH = 5
    if username == "" or password == "":
        return False
    elif len(username) < MIN_LENGTH or len(password) < MIN_LENGTH:
        return False
    else:
        return True
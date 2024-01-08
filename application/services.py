def input_validation(username, password):
    if username == "" or password == "":
        return False
    elif len(username) < 3 or len(password) < 8:
        return False
    else:
        return True
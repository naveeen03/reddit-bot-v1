import decouple


def get_client_id():
    try:
        client_id = decouple.config('CLIENT_ID')
        if client_id == "":
            print("Warning!: Client ID should not be empty!!")
            return
        return client_id
    except decouple.UndefinedValueError:
        print("Error!: missing client_id value in env var")


def get_secret_key():
    try:
        secret_key = decouple.config('SECRET_KEY')
        if secret_key == "":
            print("Warning!: Secret Key should not be empty!!")
            return
        return secret_key
    except decouple.UndefinedValueError:
        print("Error!: missing Secret Key value in env var")


def get_username():
    try:
        useraname = decouple.config('BOT_USERNAME')
        if useraname == "":
            print("Warning!: Username should not be empty!!")
            return
        return useraname
    except decouple.UndefinedValueError:
        print("Error!: missing Username value in env var")


def get_password():
    try:
        secret_key = decouple.config('BOT_PASSWORD')
        if secret_key == "":
            print("Warning!: Passsword should not be empty!!")
            return
        return secret_key
    except decouple.UndefinedValueError:
        print("Error!: missing Passsword value in env var")

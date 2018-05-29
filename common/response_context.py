

BASE_ERROR_CODE = 0

class ResponseCode(object):
    UNKNOWN_ERROR = BASE_ERROR_CODE + 0
    SUCCESS = BASE_ERROR_CODE + 1
    FAILURE = BASE_ERROR_CODE + 2
    PARAMETERS_ERROR = BASE_ERROR_CODE + 3
    EXPIRES_ERROR = BASE_ERROR_CODE + 4
    CONF_NOT_EXISTS_ERROR = BASE_ERROR_CODE + 5
    SIGN_ERROR = BASE_ERROR_CODE + 6


class ResponseMessage(object):
    UNKNOWN_ERROR = "Unexpected error."
    SUCCESS = "Successful."
    FAILURE = "Failure."
    PARAMETERS_ERROR = "Params error."
    EXPIRES_ERROR = "This request expires."
    CONF_NOT_EXISTS_ERROR = "This conf does not exist."
    SIGN_ERROR = "Sign error."
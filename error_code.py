class APP_ERRORS():
    NO_ERROR = "0"
    SUCCESS = "0"
    UNKNOWN = "-1"
    NO_REC_FOUND = "1000"
    NULL_PARAM = "4000"
    ERROR_PARAM = "4001"
    AUTH_ERROR = "9999"

    DESC = {SUCCESS: "SUCCESS",
            NO_ERROR: "NO ERROR",
            NO_REC_FOUND: "No Records Found!",
            NULL_PARAM : "Null Parameter",
            ERROR_PARAM: "Error in  Parameter",
            UNKNOWN: "Un Known Exception",
            AUTH_ERROR : "Authentication Failed"
            }

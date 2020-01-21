class NotValidatedException(Exception):
    def __init__(self):
        super(NotValidatedException, self).__init__("data should be validated before inserting into database")


class NoValueForIdException(Exception):
    def __init__(self):
        super(NoValueForIdException, self).__init__("ID cannot be None while updating")


class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class ObjectNotFoundException(Exception):
    def __init__(self, message):
        super(ObjectNotFoundException, self).__init__(message)


class ObjectAlreadyExistsException(Exception):
    def __init__(self, message):
        super(ObjectAlreadyExistsException, self).__init__(message)


class InsertNotAllowedException(Exception):
    def __init__(self, message):
        super(InsertNotAllowedException, self).__init__(message)

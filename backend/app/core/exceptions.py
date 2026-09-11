class AppError(Exception):
    code = "INTERNAL_ERROR"


class ValidationError(AppError):
    code = "VALIDATION_ERROR"


class NotFoundError(AppError):
    code = "NOT_FOUND"


class ConflictError(AppError):
    code = "CONFLICT"


class PersistenceError(AppError):
    code = "PERSISTENCE_ERROR"

    def __init__(self) -> None:
        super().__init__("No fue posible completar la operación. Intenta nuevamente.")

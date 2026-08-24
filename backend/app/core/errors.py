class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "Something went wrong.", *, code: str | None = None,
                 status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"

    def __init__(self, message: str = "The requested resource was not found.") -> None:
        super().__init__(message)


class InvalidStateError(AppError):
    status_code = 422
    code = "invalid_state"


class FileProcessingError(AppError):
    status_code = 422
    code = "file_processing_failed"


class AIProviderError(AppError):
    status_code = 502
    code = "ai_service_error"


class AITimeoutError(AIProviderError):
    status_code = 504
    code = "ai_timeout"


class AIInvalidResponseError(AIProviderError):
    status_code = 502
    code = "ai_invalid_response"

    def __init__(self, message: str = "The AI service returned an unexpected response. Please try again.") -> None:
        super().__init__(message)


class ConfigurationError(AppError):
    status_code = 503
    code = "service_configuration"

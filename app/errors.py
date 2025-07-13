from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas import CustomModel
from fastapi import Request
from pydantic import Field


class ErrorResponse(CustomModel):
    message: str = Field(examples=["Example error message"])
    code: str = Field(examples=["example:error"])


errors = {
    "transactions": {"not-found": ("Transaction not found", 404)},
    "blocks": {"not-found": ("Block not found", 404)},
}


class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message


def build_error_code(scope: str, message: str):
    return scope.replace("-", "_") + ":" + message.replace("-", "_")


def abort_handler(_: Request, exception: Abort | Exception) -> JSONResponse:
    error_code = build_error_code(exception.scope, exception.message)

    error_message = errors.get(exception.scope, {}).get(
        exception.message, ("Unknown error",)
    )[0]
    status_code = errors.get(exception.scope, {}).get(
        exception.message, (None, 400)
    )[1]

    return JSONResponse(
        status_code=status_code,
        content={
            "message": error_message,
            "code": error_code,
        },
    )


async def validation_handler(
    _: Request, exception: RequestValidationError | Exception
) -> JSONResponse:
    error_message = str(exception).replace("\n", " ").replace("   ", " ")
    return JSONResponse(
        status_code=400,
        content={
            "code": "system:validation_error",
            "message": error_message,
        },
    )

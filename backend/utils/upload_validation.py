"""Валидация загружаемых файлов: расширение и размер."""

from fastapi import HTTPException, UploadFile

MAX_IMAGE_BYTES = 15 * 1024 * 1024
MAX_ICON_BYTES = 5 * 1024 * 1024
MAX_PDF_BYTES = 50 * 1024 * 1024
MAX_VIDEO_BYTES = 2 * 1024 * 1024 * 1024

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "mkv", "avi", "m4v"}
PDF_EXTENSIONS = {"pdf"}


def file_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def check_extension(filename: str | None, allowed: set, label: str) -> None:
    if not filename:
        raise HTTPException(status_code=400, detail="Имя файла обязательно")
    if file_extension(filename) not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат {label}. Разрешены: {', '.join(sorted(allowed))}",
        )


def check_declared_size(file: UploadFile, max_bytes: int, label: str) -> None:
    """Проверяет размер, если клиент/прокси его сообщил (UploadFile.size)."""
    size = getattr(file, "size", None)
    if size is not None and size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"{label} превышает лимит {max_bytes // (1024 * 1024)} МБ",
        )


async def read_limited(file: UploadFile, max_bytes: int, label: str) -> bytes:
    """Читает файл с лимитом: больше max_bytes в память не попадёт."""
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"{label} превышает лимит {max_bytes // (1024 * 1024)} МБ",
        )
    if not data:
        raise HTTPException(status_code=400, detail=f"{label} пустой")
    return data

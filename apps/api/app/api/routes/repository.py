"""Endpoints for accepting and analyzing repository archive uploads."""

import shutil
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Annotated, Any
from zipfile import BadZipFile, ZipFile, ZipInfo, is_zipfile

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.graph import DependencyGraphBuilder
from app.services.parser import TreeSitterParser

router = APIRouter()
_CHUNK_SIZE = 1024 * 1024
_MAX_UPLOAD_BYTES = 100 * 1024 * 1024
_MAX_ARCHIVE_FILES = 10_000
_MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_repository(
    file: Annotated[UploadFile, File(description="ZIP archive of a repository")],
) -> dict[str, Any]:
    """Extract, parse, and graph a ZIP archive without retaining its contents.

    Both the uploaded archive and its extracted contents are removed once the
    response is assembled, including when validation or parsing fails.
    """

    filename = Path(file.filename or "repository.zip").name
    if Path(filename).suffix.lower() != ".zip":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only ZIP repository archives are accepted.",
        )

    upload_directory = Path(tempfile.mkdtemp(prefix="quanttwin-upload-"))
    extraction_directory = Path(tempfile.mkdtemp(prefix="quanttwin-extract-"))
    archive_path = upload_directory / "repository.zip"

    try:
        uploaded_bytes = 0
        with archive_path.open("wb") as destination:
            while chunk := await file.read(_CHUNK_SIZE):
                uploaded_bytes += len(chunk)
                if uploaded_bytes > _MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="The uploaded archive exceeds the allowed size.",
                    )
                destination.write(chunk)

        if not is_zipfile(archive_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid ZIP archive.",
            )

        _extract_archive(archive_path, extraction_directory)
        parsed_files = TreeSitterParser().parse_directory(str(extraction_directory))
        graph = DependencyGraphBuilder().build_graph(parsed_files)

        return {
            "files": [
                parsed_file.model_dump(mode="json") for parsed_file in parsed_files
            ],
            "graph": graph,
        }
    except BadZipFile as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid ZIP archive.",
        ) from error
    finally:
        await file.close()
        shutil.rmtree(upload_directory, ignore_errors=True)
        shutil.rmtree(extraction_directory, ignore_errors=True)


def _extract_archive(archive_path: Path, destination: Path) -> None:
    """Extract an archive after validating paths, links, and size limits."""

    with ZipFile(archive_path) as archive:
        members = archive.infolist()
        _validate_archive_members(members, destination)

        for member in members:
            target_path = _safe_archive_target(destination, member.filename)
            if member.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target_path.open("wb") as target:
                shutil.copyfileobj(source, target, length=_CHUNK_SIZE)


def _validate_archive_members(members: list[ZipInfo], destination: Path) -> None:
    """Reject unsafe or excessively large archives before extraction."""

    if len(members) > _MAX_ARCHIVE_FILES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The archive contains too many files.",
        )

    total_size = 0
    for member in members:
        _safe_archive_target(destination, member.filename)
        if stat.S_ISLNK(member.external_attr >> 16):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbolic links are not allowed in repository archives.",
            )
        total_size += member.file_size

    if total_size > _MAX_UNCOMPRESSED_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The archive expands beyond the allowed size.",
        )


def _safe_archive_target(destination: Path, member_name: str) -> Path:
    """Return a member path only when it remains inside the destination."""

    normalized_path = PurePosixPath(member_name.replace("\\", "/"))
    if normalized_path.is_absolute() or ".." in normalized_path.parts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The archive contains an unsafe file path.",
        )

    target_path = (destination / Path(*normalized_path.parts)).resolve()
    try:
        target_path.relative_to(destination.resolve())
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The archive contains an unsafe file path.",
        ) from error
    return target_path

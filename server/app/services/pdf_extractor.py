import io
from dataclasses import dataclass, field
from typing import Literal
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect, PDFEncryptionError, PDFNoValidXRef
from pdfminer.pdfparser import PDFSyntaxError


class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors."""
    pass


class InvalidPDFError(PDFExtractionError):
    """Raised when the uploaded file is not a valid or readable PDF."""
    pass


class EncryptedPDFError(PDFExtractionError):
    """Base exception for encrypted PDF issues."""
    pass


class PasswordRequiredError(EncryptedPDFError):
    """Raised when the PDF requires a password and none was supplied."""
    pass


class IncorrectPasswordError(EncryptedPDFError):
    """Raised when the supplied password is incorrect."""
    pass


class EmptyPDFError(PDFExtractionError):
    """Raised when the PDF file is empty (0 bytes)."""
    pass


@dataclass
class PageExtraction:
    page_number: int
    character_count: int
    word_count: int
    text: str
    has_images: bool = False
    error: str | None = None


@dataclass
class ExtractionDiagnostics:
    has_extractable_text: bool
    ocr_likely_required: bool
    is_encrypted: bool
    page_count: int
    image_count: int = 0


@dataclass
class ExtractionResult:
    filename: str
    status: Literal["success", "ocr_needed", "empty", "password_required"]
    message: str
    total_pages: int
    total_characters: int
    total_words: int
    pages: list[PageExtraction] = field(default_factory=list)
    diagnostics: ExtractionDiagnostics | None = None


def extract_pdf_preview(
    stream_or_bytes: io.BytesIO | bytes,
    filename: str = "statement.pdf",
    password: str | None = None,
) -> ExtractionResult:
    """
    Extracts text page-by-page from a PDF stream in memory.
    Supports password-protected PDFs via standard library decryption.
    Detects when no extractable text is present (scanned / image-based indicator).
    Never logs or persists passwords or sensitive document text.
    """
    if isinstance(stream_or_bytes, bytes):
        stream = io.BytesIO(stream_or_bytes)
    else:
        stream = stream_or_bytes

    stream.seek(0, io.SEEK_END)
    size = stream.tell()
    stream.seek(0)

    if size == 0:
        raise EmptyPDFError("Uploaded file is empty (0 bytes).")

    # Check standard PDF header in the first 1024 bytes
    header = stream.read(1024)
    stream.seek(0)
    if b"%PDF" not in header:
        raise InvalidPDFError("File does not contain a valid PDF header.")

    clean_password = password.strip() if (password and password.strip()) else None

    try:
        pdf_doc = pdfplumber.open(stream, password=clean_password)
    except (PDFPasswordIncorrect, PDFEncryptionError) as e:
        if not clean_password:
            raise PasswordRequiredError("This PDF is password-protected. Please enter a password.") from e
        raise IncorrectPasswordError("Incorrect password. Please verify the password and try again.") from e
    except (PDFSyntaxError, PDFNoValidXRef) as e:
        raise InvalidPDFError("Could not parse PDF. File may be corrupt or malformed.") from e
    except Exception as e:
        # Check for wrapped exceptions from pdfminer / pypdfium2
        err_str = str(e).lower()
        is_pwd_err = (
            isinstance(e, (PDFPasswordIncorrect, PDFEncryptionError))
            or (hasattr(e, "args") and e.args and isinstance(e.args[0], (PDFPasswordIncorrect, PDFEncryptionError)))
            or (hasattr(e, "__context__") and isinstance(e.__context__, (PDFPasswordIncorrect, PDFEncryptionError)))
            or "password" in err_str
            or "encrypt" in err_str
            or "decrypt" in err_str
        )
        if is_pwd_err:
            if not clean_password:
                raise PasswordRequiredError("This PDF is password-protected. Please enter a password.") from e
            raise IncorrectPasswordError("Incorrect password. Please verify the password and try again.") from e
        raise InvalidPDFError("Could not parse PDF. File may be corrupt or malformed.") from e

    with pdf_doc:
        total_pages = len(pdf_doc.pages)
        is_encrypted = (
            clean_password is not None
            or (hasattr(pdf_doc, "doc") and getattr(pdf_doc.doc, "encryption", None) is not None)
        )

        if total_pages == 0:
            return ExtractionResult(
                filename=filename,
                status="empty",
                message="The PDF contains no pages.",
                total_pages=0,
                total_characters=0,
                total_words=0,
                pages=[],
                diagnostics=ExtractionDiagnostics(
                    has_extractable_text=False,
                    ocr_likely_required=False,
                    is_encrypted=is_encrypted,
                    page_count=0,
                    image_count=0,
                ),
            )

        pages: list[PageExtraction] = []
        total_chars = 0
        total_words = 0
        total_images = 0

        for idx, page in enumerate(pdf_doc.pages):
            page_num = idx + 1
            try:
                raw_text = page.extract_text() or ""
                cleaned = raw_text.strip()
                char_cnt = len(cleaned)
                word_cnt = len(cleaned.split()) if cleaned else 0

                # Safely inspect image objects without modifying document
                img_cnt = len(page.images) if hasattr(page, "images") and page.images else 0
                total_images += img_cnt

                total_chars += char_cnt
                total_words += word_cnt

                pages.append(
                    PageExtraction(
                        page_number=page_num,
                        character_count=char_cnt,
                        word_count=word_cnt,
                        text=cleaned,
                        has_images=(img_cnt > 0),
                        error=None,
                    )
                )
            except Exception:
                # Capture page-level failure without leaking internal exception traces
                pages.append(
                    PageExtraction(
                        page_number=page_num,
                        character_count=0,
                        word_count=0,
                        text="",
                        has_images=False,
                        error=f"Text extraction failed on page {page_num}",
                    )
                )

        has_text = total_chars > 0

        if not has_text:
            # Note: Lack of extractable text is an indicator of scanned/image-based content,
            # not definitive proof.
            status: Literal["success", "ocr_needed", "empty", "password_required"] = "ocr_needed"
            message = (
                "No extractable text found. The document appears to have no digital text layer and "
                "may be a scanned or image-based PDF, which requires OCR (currently unsupported)."
            )
            ocr_likely = True
        else:
            status = "success"
            page_plural = "pages" if total_pages != 1 else "page"
            message = f"Successfully extracted text from {total_pages} {page_plural}."
            ocr_likely = False

        diagnostics = ExtractionDiagnostics(
            has_extractable_text=has_text,
            ocr_likely_required=ocr_likely,
            is_encrypted=is_encrypted,
            page_count=total_pages,
            image_count=total_images,
        )

        return ExtractionResult(
            filename=filename,
            status=status,
            message=message,
            total_pages=total_pages,
            total_characters=total_chars,
            total_words=total_words,
            pages=pages,
            diagnostics=diagnostics,
        )

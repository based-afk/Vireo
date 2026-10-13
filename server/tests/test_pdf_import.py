import io
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_extractor import (
    extract_pdf_preview,
    InvalidPDFError,
    EmptyPDFError,
    PasswordRequiredError,
    IncorrectPasswordError,
)
from app.config import MAX_UPLOAD_SIZE_BYTES


def make_synthetic_text_pdf(text: str = "HDFC Bank Statement Date: 2026-10-13 Balance: 45000.00") -> bytes:
    escaped_text = text.replace("(", "\\(").replace(")", "\\)")
    content_stream = f"BT\n/F1 12 Tf\n72 712 Td\n({escaped_text}) Tj\nET\n".encode("latin1")
    stream_len = len(content_stream)

    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(stream_len).encode("ascii") + b" >>\nstream\n"
        + content_stream +
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000224 00000 n \n"
        b"0000000318 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n397\n%%EOF"
    )
    return pdf


def make_synthetic_scanned_pdf() -> bytes:
    """A valid PDF containing a blank page without digital text (simulating an image/scanned page)."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length 0 >>\nstream\nendstream\nendobj\n"
        b"xref\n0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000204 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n253\n%%EOF"
    )


def make_synthetic_encrypted_pdf(
    text: str = "Confidential Bank Statement Balance INR 75000.00",
    password: str = "bankpass123",
) -> bytes:
    """Generates a valid encrypted PDF using pypdf for testing decryption."""
    import pypdf

    raw_pdf = make_synthetic_text_pdf(text)
    reader = pypdf.PdfReader(io.BytesIO(raw_pdf))
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


class TestPDFExtractorService(unittest.TestCase):
    def test_extract_valid_text_pdf(self):
        pdf_bytes = make_synthetic_text_pdf("HDFC Bank Statement")
        result = extract_pdf_preview(pdf_bytes, filename="statement.pdf")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.total_pages, 1)
        self.assertTrue(result.diagnostics.has_extractable_text)
        self.assertFalse(result.diagnostics.ocr_likely_required)
        self.assertFalse(result.diagnostics.is_encrypted)
        self.assertIn("HDFC Bank Statement", result.pages[0].text)

    def test_extract_scanned_style_pdf_needs_ocr(self):
        pdf_bytes = make_synthetic_scanned_pdf()
        result = extract_pdf_preview(pdf_bytes, filename="scanned.pdf")

        self.assertEqual(result.status, "ocr_needed")
        self.assertEqual(result.total_pages, 1)
        self.assertFalse(result.diagnostics.has_extractable_text)
        self.assertTrue(result.diagnostics.ocr_likely_required)
        self.assertIn("OCR", result.message)

    def test_empty_bytes_raises_empty_error(self):
        with self.assertRaises(EmptyPDFError):
            extract_pdf_preview(b"", filename="empty.pdf")

    def test_non_pdf_bytes_raises_invalid_error(self):
        with self.assertRaises(InvalidPDFError):
            extract_pdf_preview(b"This is not a PDF file.", filename="random.pdf")

    def test_malformed_pdf_raises_invalid_error(self):
        with self.assertRaises(InvalidPDFError):
            extract_pdf_preview(b"%PDF-1.4\ncorrupt body and truncated content", filename="corrupt.pdf")

    def test_encrypted_pdf_missing_password_raises_password_required(self):
        enc_bytes = make_synthetic_encrypted_pdf()
        with self.assertRaises(PasswordRequiredError):
            extract_pdf_preview(enc_bytes, filename="protected.pdf")

    def test_encrypted_pdf_incorrect_password_raises_incorrect_password(self):
        enc_bytes = make_synthetic_encrypted_pdf(password="correct123")
        with self.assertRaises(IncorrectPasswordError):
            extract_pdf_preview(enc_bytes, filename="protected.pdf", password="wrongpassword")

    def test_encrypted_pdf_correct_password_succeeds(self):
        enc_bytes = make_synthetic_encrypted_pdf(
            text="Decrypted ICICI Statement Balance 50000",
            password="correct123",
        )
        result = extract_pdf_preview(enc_bytes, filename="protected.pdf", password="correct123")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.total_pages, 1)
        self.assertTrue(result.diagnostics.is_encrypted)
        self.assertTrue(result.diagnostics.has_extractable_text)
        self.assertIn("Decrypted ICICI Statement", result.pages[0].text)


class TestPDFImportAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_preview_valid_text_pdf(self):
        pdf_bytes = make_synthetic_text_pdf("Opening Balance INR 25000.00")
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("statement.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_pages"], 1)
        self.assertTrue(data["diagnostics"]["has_extractable_text"])
        self.assertFalse(data["diagnostics"]["is_encrypted"])
        self.assertIn("Opening Balance", data["pages"][0]["text"])

    def test_preview_scanned_pdf_reports_ocr_needed(self):
        pdf_bytes = make_synthetic_scanned_pdf()
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("scanned_statement.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ocr_needed")
        self.assertTrue(data["diagnostics"]["ocr_likely_required"])
        self.assertFalse(data["diagnostics"]["has_extractable_text"])

    def test_preview_encrypted_pdf_without_password_returns_password_required(self):
        enc_bytes = make_synthetic_encrypted_pdf(password="secretpass")
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("locked.pdf", io.BytesIO(enc_bytes), "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "password_required")
        self.assertTrue(data["diagnostics"]["is_encrypted"])
        self.assertFalse(data["diagnostics"]["has_extractable_text"])

    def test_preview_encrypted_pdf_with_wrong_password_returns_400_incorrect_password(self):
        enc_bytes = make_synthetic_encrypted_pdf(password="secretpass")
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("locked.pdf", io.BytesIO(enc_bytes), "application/pdf")},
            data={"password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["code"], "incorrect_password")
        self.assertIn("incorrect password", data["error"].lower())

    def test_preview_encrypted_pdf_with_correct_password_succeeds(self):
        enc_bytes = make_synthetic_encrypted_pdf(
            text="Protected Account Statement INR 120000",
            password="secretpass",
        )
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("locked.pdf", io.BytesIO(enc_bytes), "application/pdf")},
            data={"password": "secretpass"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["diagnostics"]["is_encrypted"])
        self.assertIn("Protected Account Statement", data["pages"][0]["text"])

    def test_preview_rejects_non_pdf_extension(self):
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("statement.txt", io.BytesIO(b"sample text"), "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be a PDF document", response.json()["error"])

    def test_preview_rejects_empty_file(self):
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["error"].lower())

    def test_preview_rejects_malformed_pdf(self):
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("corrupt.pdf", io.BytesIO(b"%PDF-1.4\ncorrupted trailer"), "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("corrupt", response.json()["error"].lower())

    def test_preview_rejects_oversized_file(self):
        # Exceed MAX_UPLOAD_SIZE_BYTES
        oversized = b"%PDF-1.4\n" + b"A" * (MAX_UPLOAD_SIZE_BYTES + 512)
        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("huge.pdf", io.BytesIO(oversized), "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds the maximum limit", response.json()["error"])


if __name__ == "__main__":
    unittest.main()

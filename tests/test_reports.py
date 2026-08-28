import io

import pytest
from pypdf import PdfWriter

from app.services.reports.normalizer import normalize_report

LAB_REPORT_TEXT = """Complete Blood Count
Hemoglobin: 9.0 g/dL (Reference range: 13.0-17.0)
WBC: 11.5 x10^3/uL (4.0-11.0)
Platelets: 250 x10^3/uL (150-400)
Glucose: 92 mg/dL (70-99)
Impression: Mild anemia noted.
"""

WS_LAB_REPORT_TEXT = """Complete Blood Count
Hemoglobin 13.5 g/dL 12.0-16.0
WBC 12.8 x10^3/uL 4.0-11.0
Glucose 92 mg/dL 70-99
Platelets 210 x10^3/uL 150-400
"""


class TestReportNormalization:
    def test_extracts_lab_values_with_units(self):
        findings = normalize_report(LAB_REPORT_TEXT)
        names = [f.name for f in findings.findings]
        assert "Hemoglobin" in names
        hemoglobin = next(f for f in findings.findings if f.name == "Hemoglobin")
        assert hemoglobin.value == "9.0"
        assert hemoglobin.unit == "g/dL"
        assert hemoglobin.reference_range == "13.0-17.0"

    def test_flags_low_and_high_values(self):
        findings = normalize_report(LAB_REPORT_TEXT)
        by_name = {f.name: f for f in findings.findings}
        assert by_name["Hemoglobin"].flag == "low"
        assert by_name["WBC"].flag == "high"
        assert by_name["Glucose"].flag == "normal"

    def test_unknown_flag_without_reference(self):
        findings = normalize_report("Random value: 42 widgets\n")
        assert findings.findings[0].flag == "unknown"
        assert findings.findings[0].reference_range is None

    def test_impression_lines_captured_as_notes(self):
        findings = normalize_report(LAB_REPORT_TEXT)
        assert any("Impression" in note for note in findings.notes)

    def test_no_invention_for_unstructured_text(self):
        findings = normalize_report("The patient seems fine overall.")
        assert findings.findings == []

    def test_summary_mentions_counts(self):
        findings = normalize_report(LAB_REPORT_TEXT)
        assert "Extracted 4 structured value(s)" in findings.summary


class TestWhitespaceColumnNormalization:
    def test_extracts_whitespace_columns_with_units(self):
        findings = normalize_report(WS_LAB_REPORT_TEXT)
        by_name = {f.name: f for f in findings.findings}
        assert len(findings.findings) == 4
        assert by_name["Hemoglobin"].value == "13.5"
        assert by_name["Hemoglobin"].unit == "g/dL"
        assert by_name["Hemoglobin"].reference_range == "12.0-16.0"
        assert by_name["Hemoglobin"].flag == "normal"

    def test_flags_high_in_whitespace_format(self):
        findings = normalize_report(WS_LAB_REPORT_TEXT)
        by_name = {f.name: f for f in findings.findings}
        assert by_name["WBC"].flag == "high"
        assert by_name["Glucose"].flag == "normal"
        assert by_name["Platelets"].flag == "normal"

    def test_whitespace_line_without_reference_range_is_ignored(self):
        findings = normalize_report("Hemoglobin 13.5 g/dL\n")
        assert findings.findings == []

    def test_prose_containing_numbers_is_not_extracted(self):
        findings = normalize_report("I have had fever 3 days and feel tired\n")
        assert findings.findings == []

    def test_mixed_formats_are_both_extracted(self):
        mixed = (
            "Hemoglobin: 9.0 g/dL (13.0-17.0)\n"
            "WBC 5.0 x10^3/uL 4.0-11.0\n"
        )
        findings = normalize_report(mixed)
        by_name = {f.name: f for f in findings.findings}
        assert by_name["Hemoglobin"].flag == "low"
        assert by_name["Hemoglobin"].unit == "g/dL"
        assert by_name["WBC"].flag == "normal"

    def test_tab_separated_columns_are_extracted(self):
        findings = normalize_report("Glucose\t105\tmg/dL\t70-100\n")
        assert len(findings.findings) == 1
        finding = findings.findings[0]
        assert finding.name == "Glucose"
        assert finding.unit == "mg/dL"
        assert finding.flag == "high"


def make_blank_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


@pytest.fixture()
def uploaded_session(client, session_ids):
    return session_ids["session_id"]


class TestUploadEndpoint:
    def upload(self, client, session_id, filename, content, mime):
        return client.post(
            "/api/reports/upload",
            data={"session_id": session_id},
            files={"file": (filename, content, mime)},
        )

    def test_unsupported_file_type_rejected(self, client, uploaded_session):
        response = self.upload(client, uploaded_session, "notes.txt", b"hello", "text/plain")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "unsupported_file_type"

    def test_oversized_file_rejected(self, client, uploaded_session, monkeypatch):
        from app.core.config import get_settings

        monkeypatch.setattr(get_settings(), "upload_max_bytes", 10)
        response = self.upload(client, uploaded_session, "big.pdf", b"%PDF" + b"0" * 100, "application/pdf")
        assert response.status_code == 413
        assert response.json()["error"]["code"] == "file_too_large"

    def test_invalid_pdf_magic_rejected(self, client, uploaded_session):
        response = self.upload(client, uploaded_session, "fake.pdf", b"not a pdf at all", "application/pdf")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_pdf_file"

    def test_blank_pdf_reports_extraction_failure_clearly(self, client, uploaded_session):
        response = self.upload(
            client,
            uploaded_session,
            "scan.pdf",
            make_blank_pdf_bytes(),
            "application/pdf",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["report"]["status"] == "extraction_failed"
        assert "scanned image" in body["message"]
        assert body["report"]["extracted_findings"] is None

    def test_image_upload_is_accepted_without_fake_ocr(self, client, uploaded_session):
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
        response = self.upload(client, uploaded_session, "photo.png", png_header, "image/png")
        assert response.status_code == 200
        body = response.json()
        assert body["report"]["status"] == "stored_no_ocr"
        assert "OCR" in body["message"]

    def test_missing_session_rejected(self, client):
        response = client.post(
            "/api/reports/upload",
            data={"session_id": "f" * 32},
            files={"file": ("x.pdf", make_blank_pdf_bytes(), "application/pdf")},
        )
        assert response.status_code == 404

"""
Unit tests for the Attendance Summary download endpoints.

"Download PDF" / "Download Excel" on the Attendance Summary form stream the
summary's Daily Checkins report (same builder as the zk-daily-checkins page)
scoped to the summary's own date range and employees. These tests keep the
endpoints deterministic: correct frappe.local.response type/filename,
data fetched with the summary as the source, and PDF/Excel bytes passed
through untouched.

Run with: bench run-tests --app zkteco_attendance
"""

import unittest
from unittest.mock import MagicMock, patch

import frappe

from zkteco_attendance.zkteco_attendance.doctype.attendance_summary.attendance_summary import (
    AttendanceSummary,
)


def _summary_doc(name="ATS-0001"):
    doc = MagicMock(spec=AttendanceSummary)
    doc.name = name
    return doc


class TestDownloadSummaryPdf(unittest.TestCase):

    @patch("frappe.local", new_callable=MagicMock)
    @patch("zkteco_attendance.zkteco_attendance.doctype.attendance_summary"
           ".attendance_summary.get_pdf")
    @patch("zkteco_attendance.zkteco_attendance.doctype.attendance_summary"
           ".attendance_summary.get_daily_checkins_data")
    @patch("zkteco_attendance.zkteco_attendance.doctype.attendance_summary"
           ".attendance_summary._render_pdf_html")
    def test_pdf_streamed_with_summary_filename(self, mock_html, mock_data,
                                                mock_get_pdf, mock_local):
        doc = _summary_doc("ATS-PDF-1")
        mock_data.return_value = {"employees": [], "from_date": "2026-08-01",
                                  "to_date": "2026-08-31"}
        mock_html.return_value = "<html></html>"
        mock_get_pdf.return_value = b"%PDF-fake"

        AttendanceSummary.download_summary_pdf(doc)

        # Data is fetched from THIS summary
        mock_data.assert_called_once_with(attendance_summary="ATS-PDF-1")
        mock_get_pdf.assert_called_once_with("<html></html>")
        self.assertEqual(mock_local.response.type, "pdf")
        self.assertEqual(mock_local.response.filename, "Attendance_Summary_ATS-PDF-1.pdf")
        self.assertEqual(mock_local.response.filecontent, b"%PDF-fake")


class TestDownloadSummaryExcel(unittest.TestCase):

    @patch("frappe.local", new_callable=MagicMock)
    @patch("zkteco_attendance.zkteco_attendance.doctype.attendance_summary"
           ".attendance_summary.get_daily_checkins_data")
    @patch("zkteco_attendance.zkteco_attendance.doctype.attendance_summary"
           ".attendance_summary._build_excel_workbook")
    def test_excel_streamed_with_summary_filename(self, mock_build, mock_data,
                                                  mock_local):
        doc = _summary_doc("ATS-XLS-1")
        mock_data.return_value = {"employees": [], "from_date": "2026-08-01",
                                  "to_date": "2026-08-31"}
        mock_build.return_value = b"PK-fake-xlsx"

        AttendanceSummary.download_summary_excel(doc)

        mock_data.assert_called_once_with(attendance_summary="ATS-XLS-1")
        mock_build.assert_called_once_with({"employees": [], "from_date": "2026-08-01",
                                            "to_date": "2026-08-31"})
        self.assertEqual(mock_local.response.type, "binary")
        self.assertEqual(mock_local.response.filename, "Attendance_Summary_ATS-XLS-1.xlsx")
        self.assertEqual(mock_local.response.filecontent, b"PK-fake-xlsx")


if __name__ == "__main__":
    unittest.main()

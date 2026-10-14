import io
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.services.statement_parser import (
    parse_bank_statement_text,
    parse_date,
    parse_amount,
)
from tests.test_pdf_import import make_synthetic_text_pdf


class TestStatementParserService(unittest.TestCase):
    def test_parse_date_formats(self):
        iso, err = parse_date("01/09/2026")
        self.assertEqual(iso, "2026-09-01")
        self.assertIsNone(err)

        iso2, err2 = parse_date("15-08-2025")
        self.assertEqual(iso2, "2025-08-15")
        self.assertIsNone(err2)

        iso3, err3 = parse_date("99/99/2026")
        self.assertIsNone(iso3)
        self.assertIsNotNone(err3)

    def test_parse_amount_normalization(self):
        self.assertEqual(parse_amount("100.00"), 100.0)
        self.assertEqual(parse_amount("7,429.88"), 7429.88)
        self.assertEqual(parse_amount("1,00,000.00"), 100000.0)
        self.assertEqual(parse_amount("-"), 0.0)
        self.assertEqual(parse_amount("0.00"), 0.0)
        self.assertEqual(parse_amount("500.00 Dr"), -500.0)
        self.assertEqual(parse_amount("500.00 Cr"), 500.0)

    def test_parse_standard_withdrawal_and_deposit(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 UPI/62451234890/Groceries Payment 100.00 0.00 7,429.88
        02/09/2026 SALARY CREDIT FROM CORP 0.00 50,000.00 57,429.88
        """
        result = parse_bank_statement_text(sample_text)

        self.assertTrue(result.has_transactions)
        self.assertEqual(len(result.transactions), 2)

        # Row 1: Expense
        row1 = result.transactions[0]
        self.assertEqual(row1.row_number, 1)
        self.assertEqual(row1.date, "2026-09-01")
        self.assertEqual(row1.original_date, "01/09/2026")
        self.assertEqual(row1.narration, "UPI/62451234890/Groceries Payment")
        self.assertEqual(row1.type, "EXPENSE")
        self.assertEqual(row1.amount, 100.0)
        self.assertEqual(row1.withdrawal, 100.0)
        self.assertEqual(row1.deposit, 0.0)
        self.assertEqual(row1.closing_balance, 7429.88)
        self.assertEqual(row1.status, "valid")
        self.assertEqual(row1.issues, [])

        # Row 2: Income
        row2 = result.transactions[1]
        self.assertEqual(row2.row_number, 2)
        self.assertEqual(row2.date, "2026-09-02")
        self.assertEqual(row2.type, "INCOME")
        self.assertEqual(row2.amount, 50000.0)
        self.assertEqual(row2.withdrawal, 0.0)
        self.assertEqual(row2.deposit, 50000.0)
        self.assertEqual(row2.closing_balance, 57429.88)
        self.assertEqual(row2.status, "valid")

        # Summary
        self.assertEqual(result.summary.total_transactions, 2)
        self.assertEqual(result.summary.valid_count, 2)
        self.assertEqual(result.summary.needs_review_count, 0)
        self.assertEqual(result.summary.total_withdrawals, 100.0)
        self.assertEqual(result.summary.total_deposits, 50000.0)
        self.assertEqual(result.summary.net_change, 49900.0)

    def test_parse_multiline_narration(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 UPI/62451234890/Groceries Payment 100.00 0.00 7,429.88
        Ref: 1234567890 UPI/CR/99281
        Merchant ID: 8872134
        02/09/2026 ELECTRICITY BILL PAYMENT 850.50 0.00 6,579.38
        Consumer No: 009876231
        """
        result = parse_bank_statement_text(sample_text)

        self.assertEqual(len(result.transactions), 2)
        row1 = result.transactions[0]
        self.assertIn("Ref: 1234567890", row1.narration)
        self.assertIn("Merchant ID: 8872134", row1.narration)
        self.assertEqual(row1.amount, 100.0)
        self.assertEqual(row1.status, "valid")

        row2 = result.transactions[1]
        self.assertIn("Consumer No: 009876231", row2.narration)
        self.assertEqual(row2.amount, 850.50)
        self.assertEqual(row2.status, "valid")

    def test_parse_multiline_with_amounts_on_continuation_line(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 UPI-TRANSFER TO RAJESH KUMAR
        BANK REF NO 987654321 0.00 2,500.00 9,429.88
        """
        result = parse_bank_statement_text(sample_text)

        self.assertEqual(len(result.transactions), 1)
        row = result.transactions[0]
        self.assertEqual(row.date, "2026-09-01")
        self.assertIn("UPI-TRANSFER TO RAJESH KUMAR", row.narration)
        self.assertIn("BANK REF NO 987654321", row.narration)
        self.assertEqual(row.deposit, 2500.0)
        self.assertEqual(row.closing_balance, 9429.88)
        self.assertEqual(row.type, "INCOME")
        self.assertEqual(row.status, "valid")

    def test_repeated_headers_and_page_metadata_filtered(self):
        sample_text = """
        Account Statement - HDFC Bank
        Account Number: 50100234567890
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 GROCERY STORE 250.00 0.00 5,000.00
        Page 1 of 2
        --------------------------------------------------
        Txn Date Narration Withdrawals Deposits Closing Balance
        02/09/2026 COFFEE SHOP 120.00 0.00 4,880.00
        Page 2 of 2
        End of Statement
        """
        result = parse_bank_statement_text(sample_text)

        self.assertEqual(len(result.transactions), 2)
        self.assertEqual(result.transactions[0].date, "2026-09-01")
        self.assertEqual(result.transactions[1].date, "2026-09-02")
        self.assertNotIn("Page 1 of 2", result.transactions[0].narration)
        self.assertNotIn("Page 2 of 2", result.transactions[1].narration)
        self.assertEqual(result.summary.valid_count, 2)

    def test_malformed_and_ambiguous_rows_flagged_for_review(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 VALID PAYMENT 100.00 0.00 5,000.00
        02/09/2026 AMBIGUOUS ADJUSTMENT 50.00 50.00 5,000.00
        03/09/2026 ZERO VALUE RECORD 0.00 0.00 5,000.00
        99/99/2026 BAD DATE RECORD 150.00 0.00 4,850.00
        """
        result = parse_bank_statement_text(sample_text)

        self.assertEqual(len(result.transactions), 4)

        # Row 1 is valid
        self.assertEqual(result.transactions[0].status, "valid")

        # Row 2: both withdrawal and deposit
        self.assertEqual(result.transactions[1].status, "needs_review")
        self.assertEqual(result.transactions[1].type, "UNKNOWN")
        self.assertTrue(any("both withdrawal" in iss.lower() for iss in result.transactions[1].issues))

        # Row 3: zero financial amount
        self.assertEqual(result.transactions[2].status, "needs_review")
        self.assertTrue(any("zero financial amount" in iss.lower() for iss in result.transactions[2].issues))

        # Row 4: bad date
        self.assertEqual(result.transactions[3].status, "needs_review")
        self.assertIsNone(result.transactions[3].date)
        self.assertEqual(result.transactions[3].original_date, "99/99/2026")

        # Summary calculations only count valid rows!
        self.assertEqual(result.summary.valid_count, 1)
        self.assertEqual(result.summary.needs_review_count, 3)
        self.assertEqual(result.summary.total_withdrawals, 100.0)
        self.assertEqual(result.summary.total_deposits, 0.0)

    def test_final_statement_summary_row_with_date_excluded_from_transactions(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 UPI/62451234890/Groceries Payment 100.00 0.00 7,429.88
        02/09/2026 SALARY CREDIT FROM CORP 0.00 50,000.00 57,429.88
        30/09/2026 Net Income and Expenditure 100.00 50,000.00 57,429.88
        """
        result = parse_bank_statement_text(sample_text)

        # The summary row must be excluded from individual transactions
        self.assertEqual(len(result.transactions), 2)
        self.assertEqual(result.summary.total_transactions, 2)
        self.assertEqual(result.summary.valid_count, 2)
        self.assertEqual(result.summary.needs_review_count, 0)

        # Transactions must be row 1 and row 2 only
        self.assertEqual(result.transactions[0].narration, "UPI/62451234890/Groceries Payment")
        self.assertEqual(result.transactions[0].type, "EXPENSE")
        self.assertEqual(result.transactions[1].narration, "SALARY CREDIT FROM CORP")
        self.assertEqual(result.transactions[1].type, "INCOME")

        # Captured in optional statement summary fields
        self.assertEqual(result.summary.statement_total_withdrawals, 100.0)
        self.assertEqual(result.summary.statement_total_deposits, 50000.0)
        self.assertEqual(result.summary.statement_net_income, 49900.0)
        self.assertEqual(result.summary.statement_closing_balance, 57429.88)

    def test_final_statement_summary_row_without_date_excluded(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 UPI/Payment 100.00 0.00 7,429.88
        02/09/2026 SALARY CREDIT 0.00 50,000.00 57,429.88
        Total Withdrawals / Deposits 100.00 50,000.00 57,429.88
        """
        result = parse_bank_statement_text(sample_text)

        self.assertEqual(len(result.transactions), 2)
        self.assertEqual(result.summary.total_transactions, 2)
        self.assertEqual(result.summary.valid_count, 2)
        self.assertEqual(result.summary.needs_review_count, 0)
        self.assertNotIn("Total Withdrawals", result.transactions[1].narration)
        self.assertEqual(result.summary.statement_total_withdrawals, 100.0)
        self.assertEqual(result.summary.statement_total_deposits, 50000.0)

    def test_ordinary_transactions_with_total_or_income_in_narration_preserved(self):
        sample_text = """
        Txn Date Narration Withdrawals Deposits Closing Balance
        01/09/2026 SALARY INCOME FROM ACME CORP 0.00 50,000.00 57,429.88
        02/09/2026 TOTAL REPAIR SOLUTIONS 450.00 0.00 56,979.88
        03/09/2026 TOTAL GAS STATION 100.00 0.00 56,879.88
        04/09/2026 RENTAL INCOME PAYMENT 0.00 15,000.00 71,879.88
        05/09/2026 INCOME TAX REFUND 0.00 3,000.00 74,879.88
        30/09/2026 Net Income and Expenditure 550.00 68,000.00 74,879.88
        """
        result = parse_bank_statement_text(sample_text)

        # All 5 real transactions must be preserved!
        self.assertEqual(len(result.transactions), 5)
        self.assertEqual(result.summary.total_transactions, 5)
        self.assertEqual(result.summary.valid_count, 5)
        self.assertEqual(result.summary.needs_review_count, 0)

        narrations = [t.narration for t in result.transactions]
        self.assertIn("SALARY INCOME FROM ACME CORP", narrations)
        self.assertIn("TOTAL REPAIR SOLUTIONS", narrations)
        self.assertIn("TOTAL GAS STATION", narrations)
        self.assertIn("RENTAL INCOME PAYMENT", narrations)
        self.assertIn("INCOME TAX REFUND", narrations)

        # Summary line was excluded
        self.assertNotIn("Net Income and Expenditure", narrations)

        # Valid totals match sum of the 5 transactions
        self.assertEqual(result.summary.total_withdrawals, 550.0)
        self.assertEqual(result.summary.total_deposits, 68000.0)
        self.assertEqual(result.summary.statement_total_withdrawals, 550.0)
        self.assertEqual(result.summary.statement_total_deposits, 68000.0)

    def test_unsupported_layout_and_empty_text(self):
        empty_result = parse_bank_statement_text("")
        self.assertFalse(empty_result.has_transactions)
        self.assertEqual(len(empty_result.transactions), 0)

        unsupported_text = """
        This is an article about banking technology.
        No table headers or statement rows are present in this document.
        Machine learning and artificial intelligence in fintech.
        """
        result = parse_bank_statement_text(unsupported_text)
        self.assertFalse(result.has_transactions)
        self.assertEqual(len(result.transactions), 0)
        self.assertTrue(len(result.unparsed_lines) > 0)
        self.assertTrue(len(result.parsing_warnings) > 0)


class TestStatementImportAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_preview_returns_structured_statement(self):
        sample_statement = (
            "Txn Date Narration Withdrawals Deposits Closing Balance\n"
            "01/09/2026 UPI/62451234890/Grocery Store 100.00 0.00 7,429.88\n"
            "02/09/2026 SALARY CREDIT 0.00 45,000.00 52,429.88\n"
        )
        pdf_bytes = make_synthetic_text_pdf(sample_statement)

        response = self.client.post(
            "/api/imports/preview",
            files={"file": ("statement.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["status"], "success")
        self.assertIn("statement", data)
        statement = data["statement"]
        self.assertIsNotNone(statement)
        self.assertTrue(statement["has_transactions"])
        self.assertEqual(len(statement["transactions"]), 2)

        # Check summary
        summary = statement["summary"]
        self.assertEqual(summary["total_transactions"], 2)
        self.assertEqual(summary["valid_count"], 2)
        self.assertEqual(summary["total_withdrawals"], 100.0)
        self.assertEqual(summary["total_deposits"], 45000.0)
        self.assertEqual(summary["net_change"], 44900.0)

        # Check transactions
        t1 = statement["transactions"][0]
        self.assertEqual(t1["date"], "2026-09-01")
        self.assertEqual(t1["type"], "EXPENSE")
        self.assertEqual(t1["withdrawal"], 100.0)
        self.assertEqual(t1["closing_balance"], 7429.88)
        self.assertEqual(t1["status"], "valid")


if __name__ == "__main__":
    unittest.main()

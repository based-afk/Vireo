import re
import datetime
from dataclasses import dataclass, field
from typing import Literal

DATE_PREFIX_REGEX = re.compile(
    r"^(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}(?:-|\s+)[A-Za-z]{3}(?:-|\s+)\d{2,4})\b"
)

# Numeric token allowing Indian format commas (e.g. 1,00,000.00), standard commas (100,000.00),
# dashes (-), and optional Cr/Dr indicators
AMOUNT_TOKEN_PATTERN = r"(?:[-+]?(?:\d{1,3}(?:,\d{2,3})*|\d+)(?:\.\d{1,2})?(?:\s*(?:Cr|Dr|CR|DR))?|-)"

THREE_AMOUNTS_REGEX = re.compile(
    r"(?P<withdrawal>" + AMOUNT_TOKEN_PATTERN + r")\s+"
    r"(?P<deposit>" + AMOUNT_TOKEN_PATTERN + r")\s+"
    r"(?P<balance>" + AMOUNT_TOKEN_PATTERN + r")\s*$"
)

HEADER_KEYWORDS = [
    ("txn date", "date", "transaction date", "value date"),
    ("narration", "particulars", "description", "details", "remarks"),
    ("withdrawal", "withdrawals", "debit", "dr"),
    ("deposit", "deposits", "credit", "cr"),
    ("closing balance", "balance", "running balance"),
]

METADATA_PATTERNS = [
    re.compile(r"^\s*page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*(account\s+(number|no|statement|summary)|customer\s+name|statement\s+period|ifsc|branch|micr|cif)\b", re.IGNORECASE),
    re.compile(r"^\s*[-=_*~]{3,}\s*$"),
    re.compile(r"^\s*end\s+of\s+statement\s*$", re.IGNORECASE),
    re.compile(r"^\s*(opening\s+balance|brought\s+forward|b/f)\b", re.IGNORECASE),
    re.compile(r"^\s*(carried\s+forward|c/f)\b", re.IGNORECASE),
]


@dataclass
class ParsedTransaction:
    row_number: int
    date: str | None  # ISO "YYYY-MM-DD"
    original_date: str | None
    narration: str
    type: Literal["EXPENSE", "INCOME", "UNKNOWN"]
    amount: float
    withdrawal: float
    deposit: float
    closing_balance: float | None
    status: Literal["valid", "needs_review"]
    issues: list[str] = field(default_factory=list)


@dataclass
class StatementSummary:
    total_transactions: int = 0
    valid_count: int = 0
    needs_review_count: int = 0
    total_withdrawals: float = 0.0
    total_deposits: float = 0.0
    net_change: float = 0.0
    statement_total_withdrawals: float | None = None
    statement_total_deposits: float | None = None
    statement_net_income: float | None = None
    statement_closing_balance: float | None = None


@dataclass
class ParsedStatement:
    has_transactions: bool
    format_detected: str
    summary: StatementSummary
    transactions: list[ParsedTransaction] = field(default_factory=list)
    unparsed_lines: list[str] = field(default_factory=list)
    parsing_warnings: list[str] = field(default_factory=list)


def parse_amount(val_str: str | None) -> float | None:
    """Parses a currency amount string into a float. Returns 0.0 for dash/empty."""
    if not val_str:
        return 0.0
    cleaned = val_str.strip().replace(",", "")
    if cleaned in ("-", "", "0", "0.0", "0.00"):
        return 0.0

    is_cr = "cr" in cleaned.lower()
    is_dr = "dr" in cleaned.lower()
    num_part = re.sub(r"[^\d.-]", "", cleaned)
    try:
        val = float(num_part)
        if is_dr and val > 0:
            val = -val
        return val
    except ValueError:
        return None


def parse_date(date_str: str) -> tuple[str | None, str | None]:
    """
    Parses date string into ISO 'YYYY-MM-DD'.
    Returns (iso_date, error_message).
    """
    cleaned = date_str.strip()
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d %b %Y",
        "%d-%b-%Y",
        "%d %b %y",
        "%d-%b-%y",
        "%d %B %Y",
        "%d-%B-%Y",
    ]
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d"), None
        except ValueError:
            continue
    return None, f"Unrecognized date format: '{date_str}'"


def is_header_line(line: str) -> bool:
    """Detects if a line is a table column header line."""
    lower = line.lower()
    matches = 0
    for group in HEADER_KEYWORDS:
        if any(keyword in lower for keyword in group):
            matches += 1
    return matches >= 3


def is_metadata_or_footer(line: str) -> bool:
    """Detects if a line is page metadata, summary line or divider."""
    trimmed = line.strip()
    if not trimmed:
        return True
    for pat in METADATA_PATTERNS:
        if pat.search(trimmed):
            return True
    return False


# Explicit, conservative patterns for statement-summary labels.
# Anchored to the start of text after optional date/date-range prefix so ordinary transactions
# with words like "total" or "income" (e.g. "TOTAL REPAIR SHOP", "SALARY INCOME") are never matched.
STATEMENT_SUMMARY_LABEL_PATTERNS = [
    re.compile(
        r"^(?:statement\s+)?net\s+income(?:\s*(?:and|&|/)\s*(?:net\s*)?expenditure)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?:statement\s+)?net\s+expenditure(?:\s*(?:and|&|/)\s*(?:net\s*)?income)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^total\s+withdrawals?(?:\s*(?:and|&|/)\s*total\s+deposits?)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^total\s+deposits?(?:\s*(?:and|&|/)\s*total\s+withdrawals?)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^total\s+debits?(?:\s*(?:and|&|/)\s*total\s+credits?)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^total\s+credits?(?:\s*(?:and|&|/)\s*total\s+debits?)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?:statement\s+summary|transaction\s+totals?|statement\s+totals?|grand\s+total)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^totals?\s*[:/-]?\s*(?:[0-9-]|Cr|Dr|$)",
        re.IGNORECASE,
    ),
]

TWO_AMOUNTS_REGEX = re.compile(
    r"(?P<withdrawal>" + AMOUNT_TOKEN_PATTERN + r")\s+"
    r"(?P<deposit>" + AMOUNT_TOKEN_PATTERN + r")\s*$"
)


def is_statement_summary_line(line: str) -> bool:
    """
    Checks if a line represents a statement summary row (e.g. net income/expenditure, total withdrawals/deposits).
    Anchors to beginning of text after optional date or date-range prefix to strictly exclude real transactions
    such as 'SALARY INCOME' or 'TOTAL REPAIR'.
    """
    cleaned = line.strip()
    if not cleaned:
        return False

    # Strip optional date prefix if present (e.g. "30/09/2026 Net Income...")
    date_match = DATE_PREFIX_REGEX.match(cleaned)
    if date_match:
        cleaned = cleaned[date_match.end():].strip()

    # Also handle date range prefix (e.g. "01/09/2026 - 30/09/2026 ...")
    date_range_match = re.match(
        r"^\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*(?:to|-)\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*",
        cleaned,
        re.IGNORECASE,
    )
    if date_range_match:
        cleaned = cleaned[date_range_match.end():].strip()

    for pattern in STATEMENT_SUMMARY_LABEL_PATTERNS:
        if pattern.search(cleaned):
            return True
    return False


def extract_summary_amounts(line: str) -> dict:
    """
    Extracts recognized summary amounts from a statement-summary line.
    Returns dict with keys: withdrawals, deposits, closing_balance.
    """
    res = {"withdrawals": None, "deposits": None, "closing_balance": None}

    # 1. Try 3 amounts (Withdrawals, Deposits, Balance)
    m3 = THREE_AMOUNTS_REGEX.search(line)
    if m3:
        res["withdrawals"] = parse_amount(m3.group("withdrawal"))
        res["deposits"] = parse_amount(m3.group("deposit"))
        res["closing_balance"] = parse_amount(m3.group("balance"))
        return res

    # 2. Try 2 amounts (Withdrawals, Deposits)
    m2 = TWO_AMOUNTS_REGEX.search(line)
    if m2:
        res["withdrawals"] = parse_amount(m2.group("withdrawal"))
        res["deposits"] = parse_amount(m2.group("deposit"))
        return res

    # 3. Labeled regexes if formatted as "Withdrawals: X Deposits: Y"
    w_match = re.search(r"(?:withdrawals?|debits?|expenditure)\s*[:=]?\s*([0-9.,]+)", line, re.IGNORECASE)
    if w_match:
        res["withdrawals"] = parse_amount(w_match.group(1))

    d_match = re.search(r"(?:deposits?|credits?|income)\s*[:=]?\s*([0-9.,]+)", line, re.IGNORECASE)
    if d_match:
        res["deposits"] = parse_amount(d_match.group(1))

    b_match = re.search(r"(?:balance|closing)\s*[:=]?\s*([0-9.,]+)", line, re.IGNORECASE)
    if b_match:
        res["closing_balance"] = parse_amount(b_match.group(1))

    return res


def parse_bank_statement_text(text: str) -> ParsedStatement:
    """
    Parses bank statement text into structured transactions.
    Supports multiline narrations, repeated page headers, amount normalization,
    and flags ambiguous/malformed rows.
    """
    if not text or not text.strip():
        return ParsedStatement(
            has_transactions=False,
            format_detected="Empty",
            summary=StatementSummary(),
            transactions=[],
            unparsed_lines=[],
            parsing_warnings=["No text content to parse."],
        )

    # Normalize special PDF newline markers and carriage returns
    normalized_text = (
        text.replace("(cid:10)", "\n")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    lines = [ln.strip() for ln in normalized_text.splitlines()]
    non_empty_lines = [ln for ln in lines if ln]

    header_detected = any(is_header_line(ln) for ln in non_empty_lines)
    format_name = "Txn Date / Narration / Withdrawals / Deposits / Closing Balance" if header_detected else "Standard Bank Statement"

    raw_rows: list[dict] = []
    unparsed_lines: list[str] = []
    current_row: dict | None = None
    recognized_summary_data: dict | None = None

    for line in non_empty_lines:
        # 1. Skip repeated headers or metadata
        if is_header_line(line) or is_metadata_or_footer(line):
            continue

        # 1b. Check if this line is a statement-summary row
        if is_statement_summary_line(line):
            # Finalize previous row if pending
            if current_row is not None:
                raw_rows.append(current_row)
                current_row = None

            # Capture summary totals from line
            info = extract_summary_amounts(line)
            if recognized_summary_data is None:
                recognized_summary_data = info
            else:
                for k, v in info.items():
                    if v is not None and recognized_summary_data[k] is None:
                        recognized_summary_data[k] = v
            continue

        # 2. Check if line starts with a date
        date_match = DATE_PREFIX_REGEX.match(line)
        if date_match:
            # Finalize previous row if pending
            if current_row is not None:
                raw_rows.append(current_row)

            date_str = date_match.group("date")
            remainder = line[date_match.end():].strip()

            amounts_match = THREE_AMOUNTS_REGEX.search(remainder)
            if amounts_match:
                narration = remainder[:amounts_match.start()].strip()
                current_row = {
                    "raw_date": date_str,
                    "narration_parts": [narration] if narration else [],
                    "withdrawal_str": amounts_match.group("withdrawal"),
                    "deposit_str": amounts_match.group("deposit"),
                    "balance_str": amounts_match.group("balance"),
                    "amounts_found": True,
                }
            else:
                # Amounts might be on next line(s)
                current_row = {
                    "raw_date": date_str,
                    "narration_parts": [remainder] if remainder else [],
                    "withdrawal_str": None,
                    "deposit_str": None,
                    "balance_str": None,
                    "amounts_found": False,
                }
            continue

        # 3. Line does not start with a date
        if current_row is not None:
            # Check if this continuation line ends with the 3 amounts (if not yet found)
            if not current_row["amounts_found"]:
                amounts_match = THREE_AMOUNTS_REGEX.search(line)
                if amounts_match:
                    narration_part = line[:amounts_match.start()].strip()
                    if narration_part:
                        current_row["narration_parts"].append(narration_part)
                    current_row["withdrawal_str"] = amounts_match.group("withdrawal")
                    current_row["deposit_str"] = amounts_match.group("deposit")
                    current_row["balance_str"] = amounts_match.group("balance")
                    current_row["amounts_found"] = True
                    continue

            # Check if line is purely continuation of narration
            # e.g. reference number, UPI ID, etc.
            # Make sure it doesn't look like an entirely detached set of numbers
            current_row["narration_parts"].append(line)
        else:
            unparsed_lines.append(line)

    if current_row is not None:
        raw_rows.append(current_row)

    # Now validate and normalize all collected rows
    transactions: list[ParsedTransaction] = []
    warnings: list[str] = []

    for row in raw_rows:
        full_narration = " ".join(part for part in row["narration_parts"] if part).strip()

        # Double check if row is a statement summary (e.g. if matched as multiline)
        if is_statement_summary_line(full_narration):
            if recognized_summary_data is None:
                w_val = parse_amount(row.get("withdrawal_str"))
                d_val = parse_amount(row.get("deposit_str"))
                b_val = parse_amount(row.get("balance_str"))
                recognized_summary_data = {
                    "withdrawals": w_val,
                    "deposits": d_val,
                    "closing_balance": b_val,
                }
            continue

        row_num = len(transactions) + 1
        issues: list[str] = []

        # Date validation
        iso_date, date_err = parse_date(row["raw_date"])
        if date_err:
            issues.append(date_err)

        # Narration
        if not full_narration:
            full_narration = "Transaction"
            issues.append("Missing narration")

        # Amounts
        w_val = parse_amount(row["withdrawal_str"])
        d_val = parse_amount(row["deposit_str"])
        b_val = parse_amount(row["balance_str"])

        if w_val is None:
            issues.append(f"Invalid withdrawal amount: '{row['withdrawal_str']}'")
            w_val = 0.0
        if d_val is None:
            issues.append(f"Invalid deposit amount: '{row['deposit_str']}'")
            d_val = 0.0

        if not row["amounts_found"] and row["withdrawal_str"] is None and row["deposit_str"] is None:
            issues.append("Missing transaction amount columns")

        # Derive Type and Amount
        txn_type: Literal["EXPENSE", "INCOME", "UNKNOWN"]
        amount = 0.0

        if w_val > 0 and d_val == 0:
            txn_type = "EXPENSE"
            amount = round(w_val, 2)
        elif d_val > 0 and w_val == 0:
            txn_type = "INCOME"
            amount = round(d_val, 2)
        elif w_val == 0 and d_val == 0:
            txn_type = "UNKNOWN"
            amount = 0.0
            issues.append("Zero financial amount (both withdrawal and deposit are 0.00)")
        else:
            txn_type = "UNKNOWN"
            amount = round(w_val if w_val > 0 else d_val, 2)
            issues.append(f"Ambiguous transaction: both withdrawal ({w_val}) and deposit ({d_val}) have non-zero amounts")

        # Balance check
        if b_val is None and row["balance_str"] is not None:
            issues.append(f"Invalid closing balance: '{row['balance_str']}'")

        status: Literal["valid", "needs_review"] = "valid" if len(issues) == 0 else "needs_review"

        transactions.append(
            ParsedTransaction(
                row_number=row_num,
                date=iso_date,
                original_date=row["raw_date"],
                narration=full_narration,
                type=txn_type,
                amount=amount,
                withdrawal=round(w_val, 2),
                deposit=round(d_val, 2),
                closing_balance=round(b_val, 2) if b_val is not None else None,
                status=status,
                issues=issues,
            )
        )

    # Calculate summary ONLY from successfully parsed ('valid') rows
    valid_rows = [t for t in transactions if t.status == "valid"]
    valid_count = len(valid_rows)
    needs_review_count = len(transactions) - valid_count

    total_withdrawals = round(sum(t.withdrawal for t in valid_rows), 2)
    total_deposits = round(sum(t.deposit for t in valid_rows), 2)
    net_change = round(total_deposits - total_withdrawals, 2)

    statement_total_w = recognized_summary_data.get("withdrawals") if recognized_summary_data else None
    statement_total_d = recognized_summary_data.get("deposits") if recognized_summary_data else None
    statement_net_inc = (
        round(statement_total_d - statement_total_w, 2)
        if (statement_total_w is not None and statement_total_d is not None)
        else None
    )
    statement_balance = recognized_summary_data.get("closing_balance") if recognized_summary_data else None

    summary = StatementSummary(
        total_transactions=len(transactions),
        valid_count=valid_count,
        needs_review_count=needs_review_count,
        total_withdrawals=total_withdrawals,
        total_deposits=total_deposits,
        net_change=net_change,
        statement_total_withdrawals=statement_total_w,
        statement_total_deposits=statement_total_d,
        statement_net_income=statement_net_inc,
        statement_closing_balance=statement_balance,
    )

    has_transactions = len(transactions) > 0
    if not has_transactions:
        warnings.append("No transaction rows matching standard bank statement format were found.")

    if needs_review_count > 0:
        warnings.append(f"{needs_review_count} row(s) require review due to parsing issues or ambiguous amounts.")

    return ParsedStatement(
        has_transactions=has_transactions,
        format_detected=format_name if has_transactions else "Unknown / Unsupported",
        summary=summary,
        transactions=transactions,
        unparsed_lines=unparsed_lines,
        parsing_warnings=warnings,
    )

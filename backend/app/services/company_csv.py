import csv
from dataclasses import dataclass
from io import StringIO

from pydantic import ValidationError

from app.schemas.companies import CompanyCreate, CsvValidationIssue

CANONICAL_COLUMNS = tuple(CompanyCreate.model_fields)
REQUIRED_COLUMNS = {"name"}
LIST_COLUMNS = {"cloud_usage", "regulatory_context", "tags"}


@dataclass
class CompanyCsvError(ValueError):
    code: str
    issues: list[CsvValidationIssue]


def parse_company_csv(content: bytes) -> list[CompanyCreate]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CompanyCsvError(
            "invalid_encoding", [CsvValidationIssue(code="invalid_encoding")]
        ) from exc

    try:
        reader = csv.DictReader(StringIO(text), restkey="__extra_columns__")
        headers = reader.fieldnames
    except csv.Error as exc:
        raise CompanyCsvError("invalid_csv", [CsvValidationIssue(code="invalid_csv")]) from exc
    if headers is None:
        raise CompanyCsvError("missing_header", [CsvValidationIssue(code="missing_header")])

    duplicate_headers = sorted({header for header in headers if headers.count(header) > 1})
    unknown_headers = sorted(set(headers) - set(CANONICAL_COLUMNS))
    issues = [
        CsvValidationIssue(field=header, code="duplicate_header") for header in duplicate_headers
    ]
    issues.extend(
        CsvValidationIssue(field=header, code="unknown_header") for header in unknown_headers
    )
    issues.extend(
        CsvValidationIssue(field=header, code="missing_required_header")
        for header in sorted(REQUIRED_COLUMNS - set(headers))
    )
    if issues:
        raise CompanyCsvError("invalid_headers", issues)

    companies: list[CompanyCreate] = []
    row_keys: set[tuple[str, str | None]] = set()
    try:
        for row_number, row in enumerate(reader, start=2):
            if row.get("__extra_columns__"):
                raise CompanyCsvError(
                    "invalid_row", [CsvValidationIssue(row=row_number, code="extra_columns")]
                )
            values = {
                key: value.strip()
                for key, value in row.items()
                if key in CANONICAL_COLUMNS and value is not None and value.strip()
            }
            for key in LIST_COLUMNS:
                if key in values:
                    values[key] = [item.strip() for item in values[key].split("|") if item.strip()]
            try:
                company = CompanyCreate.model_validate(values)
            except ValidationError as exc:
                validation_issues = [
                    CsvValidationIssue(
                        row=row_number,
                        field=str(error["loc"][0]) if error["loc"] else None,
                        code=str(error["type"]),
                    )
                    for error in exc.errors()
                ]
                raise CompanyCsvError("invalid_rows", validation_issues) from exc
            key = (company.name.casefold(), company.domain.casefold() if company.domain else None)
            if key in row_keys:
                raise CompanyCsvError(
                    "duplicate_rows", [CsvValidationIssue(row=row_number, code="duplicate_row")]
                )
            row_keys.add(key)
            companies.append(company)
    except csv.Error as exc:
        raise CompanyCsvError("invalid_csv", [CsvValidationIssue(code="invalid_csv")]) from exc
    if not companies:
        raise CompanyCsvError("empty_file", [CsvValidationIssue(code="empty_file")])
    return companies


def export_company_csv(companies: list[CompanyCreate]) -> bytes:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CANONICAL_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for company in companies:
        row = company.model_dump(mode="json")
        for key in LIST_COLUMNS:
            row[key] = "|".join(row[key])
        writer.writerow(row)
    return output.getvalue().encode("utf-8-sig")

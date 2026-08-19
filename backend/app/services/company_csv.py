import csv
from io import StringIO

from pydantic import ValidationError

from app.schemas.companies import CompanyCreate

REQUIRED_COLUMNS = {"name"}
LIST_COLUMNS = {"cloud_usage", "regulatory_context", "tags"}


def parse_company_csv(content: bytes) -> list[CompanyCreate]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc
    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
        raise ValueError("CSV must include a name column.")
    companies: list[CompanyCreate] = []
    for row_number, row in enumerate(reader, start=2):
        values = {
            key: value.strip()
            for key, value in row.items()
            if key and value and value.strip()
        }
        for key in LIST_COLUMNS:
            if key in values:
                values[key] = [item.strip() for item in values[key].split("|") if item.strip()]
        for key in ("employee_count",):
            if key in values:
                values[key] = int(values[key])
        for key in ("annual_revenue_usd",):
            if key in values:
                values[key] = float(values[key])
        try:
            companies.append(CompanyCreate.model_validate(values))
        except (ValidationError, ValueError) as exc:
            raise ValueError(f"CSV row {row_number} is invalid: {exc}") from exc
    if not companies:
        raise ValueError("CSV must contain at least one company.")
    return companies


def export_company_csv(companies: list[CompanyCreate]) -> str:
    fieldnames = list(CompanyCreate.model_fields)
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for company in companies:
        row = company.model_dump()
        for key in LIST_COLUMNS:
            row[key] = "|".join(row[key])
        writer.writerow(row)
    return output.getvalue()

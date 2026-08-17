import re
import zlib
from html import unescape
from textwrap import wrap


def render_pdf_bytes(title: str, html: str) -> bytes:
    source = f"{title}\n\nGenerated from approved HTML report context.\n\n{html}"
    pages = _page_chunks(_pdf_lines(source))
    font_object_id = 3 + len(pages) * 2
    page_object_ids = [3 + index * 2 for index in range(len(pages))]
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_object_ids)}] "
            f"/Count {len(pages)} >>"
        ).encode(),
    ]
    for index, lines in enumerate(pages):
        page_id = page_object_ids[index]
        content_id = page_id + 1
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode()
        )
        stream = _page_stream(lines)
        compressed = zlib.compress(stream)
        objects.append(
            b"<< /Length %d /Filter /FlateDecode >>\nstream\n%s\nendstream"
            % (len(compressed), compressed)
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())

    output.extend(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(output)


def _pdf_lines(value: str) -> list[str]:
    value = re.sub(r"<(?:style|script)[^>]*>.*?</(?:style|script)>", "", value, flags=re.I | re.S)
    text = re.sub(r"</(?:article|h[1-4]|li|p|ul)>", "\n", value, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    lines = []
    for paragraph in unescape(text).splitlines():
        cleaned = " ".join(paragraph.split())
        if cleaned:
            lines.extend(wrap(cleaned, width=88) or [cleaned])
    return lines or ["Report content was unavailable."]


def _page_chunks(lines: list[str]) -> list[list[str]]:
    return [lines[index : index + 48] for index in range(0, len(lines), 48)]


def _page_stream(lines: list[str]) -> bytes:
    escaped_lines = [
        "(" + line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj T*"
        for line in lines
    ]
    return ("BT /F1 10 Tf 50 760 Td 14 TL\n" + "\n".join(escaped_lines) + "\nET").encode(
        "latin-1", errors="replace"
    )

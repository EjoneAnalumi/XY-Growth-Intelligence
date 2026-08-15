import zlib


def render_pdf_bytes(title: str, html: str) -> bytes:
    text = _pdf_text(f"{title}\n\nGenerated from approved HTML report context.\n\n{html}")
    stream = f"BT /F1 10 Tf 50 760 Td {text} Tj ET".encode("latin-1", errors="replace")
    compressed = zlib.compress(stream)

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d /Filter /FlateDecode >>\nstream\n%s\nendstream"
        % (len(compressed), compressed),
    ]

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


def _pdf_text(value: str) -> str:
    compact = " ".join(value.replace("\n", " ").split())
    compact = compact[:1800]
    return "(" + compact.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ")"

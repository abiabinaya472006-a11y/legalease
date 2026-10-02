"""Text sanitization tests."""

from backend.utils.sanitizers import escape_html, sanitize_filename, sanitize_text


def test_sanitize_removes_control_chars():
    dirty = "Hello\x00World\x07!"
    assert sanitize_text(dirty) == "HelloWorld!"


def test_sanitize_normalizes_newlines():
    text = "a\r\nb\rc\n\n\n\n\nd"
    cleaned = sanitize_text(text)
    assert "\r" not in cleaned
    assert "\n\n\n\n" not in cleaned


def test_sanitize_truncates():
    text = "x" * 100
    assert len(sanitize_text(text, max_length=10)) == 10


def test_escape_html():
    assert escape_html("<script>alert(1)</script>") == (
        "&lt;script&gt;alert(1)&lt;/script&gt;"
    )


def test_sanitize_filename():
    assert sanitize_filename("My NDA / Draft!.docx") == "My_NDA_Draftdocx"
    assert sanitize_filename("???") == "document"

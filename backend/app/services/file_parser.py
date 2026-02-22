import re
from pathlib import Path


def extract_text_from_txt(content: bytes, encoding: str = "utf-8") -> str:
    try:
        return content.decode(encoding)
    except UnicodeDecodeError:
        return content.decode("latin-2", errors="replace")


def extract_text_from_pdf(content: bytes) -> str:
    try:
        import pypdf
        import io

        reader = pypdf.PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    except ImportError:
        raise ValueError("Brak biblioteki pypdf. Uruchom: pip install pypdf")
    except Exception as e:
        raise ValueError(f"Błąd parsowania PDF: {e}")


def extract_text_from_docx(content: bytes) -> str:
    try:
        import docx
        import io

        doc = docx.Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    except ImportError:
        raise ValueError("Brak biblioteki python-docx. Uruchom: pip install python-docx")
    except Exception as e:
        raise ValueError(f"Błąd parsowania DOCX: {e}")


def clean_text(text: str) -> str:
    """
    Czyści tekst po ekstrakcji:
    - Usuwa nadmiarowe białe znaki
    - Usuwa znaki specjalne PDF (łamanie wierszy mid-word)
    - Normalizuje końce linii
    """
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    text = re.sub(r"-\n([a-ząęóśłżźćń])", r"\1", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def extract_text(filename: str, content: bytes) -> str:
    """
    Główna funkcja — wykrywa format po rozszerzeniu i ekstrahuje tekst.

    Args:
        filename: nazwa pliku z rozszerzeniem
        content: zawartość pliku jako bytes

    Returns:
        Czysty tekst do analizy

    Raises:
        ValueError: gdy format nieobsługiwany lub błąd parsowania
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        text = extract_text_from_txt(content)
    elif suffix == ".pdf":
        text = extract_text_from_pdf(content)
    elif suffix in (".docx", ".doc"):
        text = extract_text_from_docx(content)
    else:
        raise ValueError(
            f"Nieobsługiwany format pliku: {suffix}. "
            f"Obsługiwane: .txt, .pdf, .docx"
        )

    text = clean_text(text)

    if len(text) < 50:
        raise ValueError(
            f"Wyekstrahowany tekst jest zbyt krótki ({len(text)} znaków). "
            f"Sprawdź czy plik zawiera tekst."
        )

    return text
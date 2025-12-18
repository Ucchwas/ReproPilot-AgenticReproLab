from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel, Field
from pypdf import PdfReader


class PDFReadArgs(BaseModel):
    path: str = Field(..., description="Path to a local PDF file")


@dataclass
class PDFReadTool:
    name: str = "read_pdf_text"
    description: str = "Extracts text from a local PDF (research paper)."
    Args = PDFReadArgs

    def run(self, args: PDFReadArgs) -> str:
        p = Path(args.path)
        if not p.exists():
            raise FileNotFoundError(f"PDF not found: {p}")
        reader = PdfReader(str(p))
        pages = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            pages.append(f"\n--- PAGE {i+1} ---\n{txt}")
        return "\n".join(pages)

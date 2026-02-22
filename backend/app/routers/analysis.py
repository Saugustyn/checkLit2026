import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis
from app.schemas import (
    AnalysisRequest, AnalysisResponse, AnalysisListItem,
    CompareRequest, CompareResponse,
    AIDetectionResult, StylometryResult, QualityResult
)
from app.services.stylometry import analyze_stylometry
from app.services.nlp_service import analyze_quality
from app.services.ai_detector import detect_ai
from app.services.file_parser import extract_text

router = APIRouter()


def run_analysis_pipeline(text: str, db: Session) -> AnalysisResponse:

    if len(text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Tekst jest zbyt krótki. Minimalna długość to 50 znaków."
        )
    if len(text) > 500_000:
        raise HTTPException(
            status_code=400,
            detail="Tekst jest zbyt długi. Maksymalna długość to 500 000 znaków (~10 stron A4)."
        )

    ai_result         = detect_ai(text)
    stylometry_result = analyze_stylometry(text)
    quality_result    = analyze_quality(text)

    db_analysis = Analysis(
        text_preview=text[:500],
        full_text=text,                         
        text_length=len(text),
        ai_probability=ai_result["ai_probability"],
        ttr=stylometry_result["ttr"],
        avg_sentence_length=stylometry_result["avg_sentence_length"],
        lexical_density=stylometry_result["lexical_density"],
        entropy=stylometry_result["entropy"],
        flesch_score=quality_result["flesch_score"],
        vocab_richness=stylometry_result["vocab_richness"],
        full_results=json.dumps({
            "ai": ai_result,
            "stylometry": stylometry_result,
            "quality": quality_result
        }, ensure_ascii=False)
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    return AnalysisResponse(
        id=db_analysis.id,
        created_at=db_analysis.created_at,
        text_preview=db_analysis.text_preview,
        text_length=db_analysis.text_length,
        full_text=text,
        ai_detection=AIDetectionResult(**ai_result),
        stylometry=StylometryResult(**stylometry_result),
        quality=QualityResult(**quality_result)
    )


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_text(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analizuje tekst wklejony bezpośrednio w polu tekstowym.
    Obsługuje teksty do ~10 stron (500 000 znaków).
    """
    return run_analysis_pipeline(request.text.strip(), db)



@router.post("/analyze-file", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Przyjmuje plik .txt, .pdf lub .docx, ekstrahuje z niego tekst
    i przeprowadza pełną analizę.

    Limit: 10MB na plik (~10+ stron A4 w PDF).
    """
    MAX_SIZE = 10 * 1024 * 1024
    content = await file.read()

    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Plik jest zbyt duży ({len(content) // 1024}KB). Maksymalny rozmiar: 10MB."
        )

    try:
        text = extract_text(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return run_analysis_pipeline(text, db)



@router.get("/history", response_model=list[AnalysisListItem])
def get_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    analyses = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return analyses


@router.get("/results/{analysis_id}", response_model=AnalysisResponse)
def get_result(analysis_id: int, db: Session = Depends(get_db)):
    """Pobiera wyniki konkretnej analizy po ID."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analiza nie znaleziona")

    full = json.loads(analysis.full_results)

    return AnalysisResponse(
        id=analysis.id,
        created_at=analysis.created_at,
        text_preview=analysis.text_preview,
        text_length=analysis.text_length,
        full_text=analysis.full_text,
        ai_detection=AIDetectionResult(**full["ai"]),
        stylometry=StylometryResult(**full["stylometry"]),
        quality=QualityResult(**full["quality"])
    )


@router.post("/compare", response_model=CompareResponse)
def compare_texts(request: CompareRequest):
    """Porównuje dwa teksty stylometrycznie."""
    result_a = analyze_stylometry(request.text_a)
    result_b = analyze_stylometry(request.text_b)

    metrics = ["ttr", "avg_sentence_length", "lexical_density", "entropy"]
    diffs = []
    for m in metrics:
        a_val = result_a.get(m, 0)
        b_val = result_b.get(m, 0)
        max_val = max(abs(a_val), abs(b_val), 0.001)
        diffs.append(abs(a_val - b_val) / max_val)

    similarity = round(1.0 - (sum(diffs) / len(diffs)), 4)

    return CompareResponse(
        text_a=StylometryResult(**result_a),
        text_b=StylometryResult(**result_b),
        similarity_score=max(0.0, min(1.0, similarity))
    )


@router.delete("/history/{analysis_id}")
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Usuwa analizę z historii."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiza nie znaleziona")
    db.delete(analysis)
    db.commit()
    return {"message": "Usunięto"}


@router.get("/results/{analysis_id}/text")
def download_text(analysis_id: int, db: Session = Depends(get_db)):
    """
    Zwraca oryginalny tekst analizy jako plik .txt do pobrania.
    Jeśli pełny tekst nie jest dostępny (stare wpisy), zwraca podgląd.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analiza nie znaleziona")

    text_content = analysis.full_text or analysis.text_preview or ""

    return PlainTextResponse(
        content=text_content,
        headers={
            "Content-Disposition": f'attachment; filename="tekst_analiza_{analysis_id}.txt"',
            "Content-Type": "text/plain; charset=utf-8"
        }
    )


@router.get("/results/{analysis_id}/export")
def export_report(analysis_id: int, db: Session = Depends(get_db)):
    """
    Eksportuje pełny raport analizy jako JSON do pobrania.
    Zawiera wszystkie metryki, metadane i oryginalny tekst.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analiza nie znaleziona")

    full = json.loads(analysis.full_results)

    report = {
        "meta": {
            "id": analysis.id,
            "created_at": analysis.created_at.isoformat(),
            "text_length": analysis.text_length,
            "platform": "checkLit – Literary Analyzer",
        },
        "text_preview": analysis.text_preview,
        "ai_detection": full["ai"],
        "stylometry": full["stylometry"],
        "quality": full["quality"],
    }

    return JSONResponse(
        content=report,
        headers={
            "Content-Disposition": f'attachment; filename="raport_analiza_{analysis_id}.json"'
        }
    )
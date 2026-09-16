import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from sidecar.classifier import get_classifier

# Configurações de Log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sidecar_server")

# Lifespan: Executa código no startup e shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando servidor Sidecar. Carregando modelo SigLIP...")
    classifier = get_classifier()
    logger.info(f"Modelo carregado e pronto para uso no dispositivo: {classifier.device}")
    yield
    logger.info("Encerrando servidor Sidecar...")

app = FastAPI(
    title="PhotoOrganizer Sidecar API",
    description="API interna para classificação visual (zero-shot) de fotos locais.",
    version="1.0.0",
    lifespan=lifespan
)

class ClassifyRequest(BaseModel):
    path: str

@app.get("/health")
async def health():
    """Retorna o status do servidor e em qual hardware o modelo está rodando."""
    classifier = get_classifier()
    return {
        "status": "ready" if classifier.is_ready else "loading",
        "device": str(classifier.device)
    }

@app.post("/classify")
async def classify(request: ClassifyRequest):
    """Recebe o caminho absoluto de uma imagem e retorna sua classificação na taxonomia."""
    image_path = Path(request.path)
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {image_path}")
    if not image_path.is_file():
        raise HTTPException(status_code=400, detail=f"O caminho fornecido não é um arquivo: {image_path}")

    classifier = get_classifier()
    if not classifier.is_ready:
        raise HTTPException(status_code=503, detail="O modelo ainda está sendo carregado.")

    try:
        scores = classifier.classify_image(image_path)
        results = classifier.evaluate_tags(scores)
        return results
    except Exception as e:
        logger.error(f"Erro na classificação da imagem {request.path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Inicia o servidor FastAPI do sidecar.")
    parser.add_argument("--port", type=int, default=8000, help="Porta para o servidor escutar (padrão: 8000).")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host (padrão: 127.0.0.1).")
    args = parser.parse_args()

    logger.info(f"Iniciando uvicorn em {args.host}:{args.port}...")
    uvicorn.run("sidecar.server:app", host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()

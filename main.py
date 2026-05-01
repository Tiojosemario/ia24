from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from google.cloud import firestore
import uuid

app = FastAPI()

# Inicializa Firestore
db = firestore.Client()

# Modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Configura caminho do Tesseract no Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------------------
# Função para processar PDF (texto + OCR)
# -------------------------------
def process_pdf(file_path, doc_id=None):
    text = ""

    try:
        # Primeiro tenta extrair texto com PyPDF2
        reader = PyPDF2.PdfReader(open(file_path, "rb"))
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    except:
        pass

    # Se não achou texto, usa OCR
    if not text.strip():
        images = convert_from_path(file_path)
        for img in images:
            text += pytesseract.image_to_string(img)

    if not text.strip():
        raise ValueError("PDF sem texto legível")

    # Dividir em chunks de 500 caracteres
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    # Gerar embeddings e salvar no Firestore
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        db.collection("documentos").add({
            "doc_id": doc_id or str(uuid.uuid4()),
            "chunk_id": i,
            "texto": chunk,
            "embedding": embedding
        })

# -------------------------------
# Função para consulta
# -------------------------------
def query_firestore(pergunta, top_k=3):
    pergunta_emb = model.encode(pergunta).tolist()
    pergunta_emb = np.array(pergunta_emb)

    docs = db.collection("documentos").stream()
    resultados = []
    for doc in docs:
        data = doc.to_dict()
        emb = np.array(data["embedding"])
        # Similaridade coseno
        sim = np.dot(pergunta_emb, emb) / (np.linalg.norm(pergunta_emb) * np.linalg.norm(emb))
        resultados.append((sim, data["texto"]))

    # Ordenar por relevância
    resultados.sort(key=lambda x: x[0], reverse=True)
    return [texto for _, texto in resultados[:top_k]]

# -------------------------------
# Endpoints FastAPI
# -------------------------------
class ChatRequest(BaseModel):
    texto: str
    perfil: str

@app.post("/chat")
def chat(req: ChatRequest):
    trechos = query_firestore(req.texto)
    resposta = f"Baseado nos documentos, encontrei:\n\n" + "\n---\n".join(trechos)
    return {"resposta": resposta}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = f"./{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    process_pdf(file_path, doc_id=file.filename)
    return {"status": "arquivo processado com sucesso", "nome": file.filename}

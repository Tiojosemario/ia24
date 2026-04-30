from fastapi import FastAPI, UploadFile, File
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa Firebase com o arquivo de credenciais
cred = credentials.Certificate("firebase.json")  # nome do seu arquivo JSON
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "API rodando com sucesso!"}

@app.post("/chat")
async def chat(msg: dict):
    try:
        texto = msg["texto"]
        perfil = msg.get("perfil", "desconhecido")  # opcional: perfil enviado junto
        resposta = f"Simulação de resposta para: {texto}"

        # Salva no Firestore
        db.collection("mensagens").add({
            "texto": texto,
            "resposta": resposta,
            "perfil": perfil
        })

        return {"resposta": resposta}
    except Exception as e:
        return {"erro": str(e)}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        conteudo = await file.read()

        # Salva metadados no Firestore
        db.collection("uploads").add({
            "nome": file.filename,
            "tamanho": len(conteudo)
        })

        return {"status": "arquivo recebido", "tamanho": len(conteudo)}
    except Exception as e:
        return {"erro": str(e)}

@app.post("/url")
async def url(data: dict):
    try:
        link = data["url"]

        # Salva histórico de links no Firestore
        db.collection("urls").add({
            "url": link
        })

        return {"status": f"conteúdo de {link} processado"}
    except Exception as e:
        return {"erro": str(e)}

@app.post("/perfil")
async def perfil(data: dict):
    try:
        perfil = data["perfil"]
        db.collection("usuarios").add({"perfil": perfil})
        return {"status": f"Perfil {perfil} salvo com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}


from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "API rodando com sucesso!"}

@app.post("/chat")
async def chat(msg: dict):
    return {"resposta": f"Simulação de resposta para: {msg['texto']}"}

@app.post("/upload")
async def upload(file: UploadFile):
    conteudo = await file.read()
    return {"status": "arquivo recebido", "tamanho": len(conteudo)}

@app.post("/url")
async def url(data: dict):
    link = data["url"]
    return {"status": f"conteúdo de {link} processado"}

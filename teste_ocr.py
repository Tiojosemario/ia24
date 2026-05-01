import pytesseract
from PIL import Image

# Configura caminho do executável
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Abra uma imagem com texto
img = Image.open("teste.png")

# Extrai texto
texto = pytesseract.image_to_string(img)
print(texto)

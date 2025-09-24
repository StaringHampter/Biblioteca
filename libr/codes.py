import random
import barcode
from barcode.writer import ImageWriter
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.conf import settings

def generar_EAN():
	st = ""
	for i in range(0,12):
		n = random.randint(0,9)
		n = str(n)
		st += n
		print(st)
	return st



def generar_barcode1(code, nombre, media_path="codigos"):
	customs = {'module': 15}
	codigo = barcode.get('EAN13', code, writer=ImageWriter())
	imagen = BytesIO()
	codigo.write(imagen, options=customs)
	imagen.seek(0)

	barcode_imagen = Image.open(imagen)
	ancho, alto = barcode_imagen.size
	alton = alto + 60
	canvas = Image.new("RGB", (ancho, alton), "white")
	canvas.paste(barcode_imagen, (0, 0))

	dibujo = ImageDraw.Draw(canvas)
	try:
		font = ImageFont.truetype("arial.ttf", 20)
	except:
		font = ImageFont.load_default()
	dibujo.text((10, alto + 10), nombre, fill="black", font=font)
	name = nombre.replace(" ","_")
	if not os.path.exists(media_path):
		os.mkdir(media_path)
	filename=f"{name}.jpeg"
	path=os.path.join(settings.MEDIA_ROOT,media_path, filename)
	canvas.save(path, "JPEG")
	return path

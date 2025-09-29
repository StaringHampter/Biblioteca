from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.shortcuts import render, redirect
import json
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseRedirect
import requests
from .models import Libro, Estudiante, Prestamo, Maestro, Prestamo_Maestro
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from io import BytesIO
from django.urls import reverse
from reportlab.lib import colors
from django.db.models import Q
from . import forms, codes
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from django.utils.text import slugify
# Create your views here.

#Posible sistema de logins futuro
def login_view(request):
	if request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]

                #print(f"Login attempt: {username}")
		try:
			user = User.objects.get(username=username)
                       # print(f"User {username} found in database")

			user = authenticate(request, username=username, password=password)
                        #print(f"Authentication result: {user}")

			if user is None:
				existing_user = User.objects.get(username=username)
				is_correct_password = existing_user.check_password(password)
                                #print(f"Manual password check result: {is_correct_password}")
				return render(request, "network/login.html", {"message": "Invalid username and/or password."})
			if user is not None:
				login(request, user)
                                #print("Login successful")
				return HttpResponseRedirect(reverse("index"))

		except User.DoesNotExist:
                #        print(f"User {username} not found")
			return render(request, "network/login.html", {"message": "User does not exist."})
		except Exception as e:
                #        print(f"Unexpected error: {e}")
			return render(request, "network/login.html", {"message": "An error occurred during login."})

	return render(request, "libr/login.html")

ALLOWED_USERNAME = "bibliotecario"   #admin

#Login con usuario maestro/admin
class SingleUserLoginView(LoginView):
	template_name = "libr/login.html"

	def form_valid(self, form):
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')
		if username != ALLOWED_USERNAME:
			form.add_error(None, "Acceso denegado.")
			return self.form_invalid(form)
		return super().form_valid(form)

def logout_view(request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


def index(request):
	return render(request, "libr/index.html")


def agregar_libro(request):
	return render(request, "libr/add_books.html")
	

#Trae los datos del sitio y los retorna en formato json
@login_required
@csrf_exempt
def buscar_libro(request):
	isbn = request.POST.get("SearchISBN")
	print(isbn)
	headers = {"User Agent": "copodenieve9001@gmail.com"}
	url = f"https://openlibrary.org/search.json?isbn={isbn}"
	try:
		resp = requests.get(url, headers)
		data = resp.json()
		resultados = []
		for doc in data.get("docs", []):
			resultados.append({
			"titulo": doc.get("title", "no encontrado"),
			"autor": " ,".join(doc.get("author_name", [])),
			"año": doc.get("first_publish_year", "N/A"),
			"isbn": isbn,
			"link": f"https://openlibrary.org{doc.get('key')}" if doc.get('key') else "N/A"}	
			)
		print(resultados)
		request.session["resultados"] = resultados

		return JsonResponse({ "resultados": resultados, "exito":True })
	except Exception as e:
		return JsonResponse({"error": str(e)}, status=500)

#Filtra en base a la query al usuario
def buscar_usuario(request):
	mensaje = None
	if request.method == "GET":
		nombre = request.GET.get("nombre")
		maestro = Maestro.objects.filter(Q(nombre__icontains=nombre))
		print(maestro)
		alumno = Estudiante.objects.filter(Q(nombre__icontains=nombre))
		print(alumno)
		resp = []
		for m in maestro:
			resp.append(m)

		for a in alumno:
			resp.append(a)

		if not resp:
			mensaje = "No resultados encontrados."

	return render(request, "libr/admin.html", {"page_obj":resp, "message": mensaje})


#Renderiza todos los libros
def inventario(request):
	libros = Libro.objects.all().order_by('titulo')
	p = Paginator(libros, 10)
	page = request.GET.get("page")
	print(page)
	libros = p.get_page(page)
	mensaje = None
	return render(request, "libr/inventario.html", {"libros": libros, "mensaje":mensaje})

#JS les da un indice a los resultados del API, esta función pasa los datos del libro escogido a la plantilla para revisar y agregar antes de ingresarlo a la base de datos
@login_required
@csrf_exempt
def confirmar_libro(request, index):
	resultados = request.session.get("resultados", [])
	print(resultados)
	if 0 <= index < len(resultados):
		libro = resultados[index]
		return render(request, "libr/confirmar.html", {"libro": libro})
	return JsonResponse({"error": "Índice inválido"}, status=400)


def agregarBaseDatos(request):
	if request.method == "POST":
		titulo = request.POST.get("titulo")
		autor = request.POST.get("autor")
		año = request.POST.get("año")
		isbn = request.POST.get("isbn")
		link = request.POST.get("link")
		cantidad = request.POST.get("cantidad")
		estante = request.POST.get("estante")
		estanteria = request.POST.get("estanteria")
		if all([titulo, autor, año, isbn, link, cantidad, estante, estanteria]) != None:
			mensaje = ""
			try:
				Libro.objects.create(titulo=titulo, autor=autor, isbn=isbn, año=año, link=link, cantidad=cantidad, estante=estante,
				estanteria=estanteria)
				mensaje = "Libro Guardado con Éxito"
			except Exception as e:
				mensaje = f"Error al agregar a la base de datos. Algún campo está vacío. Por favor, intente de nuevo."
				print(e)
				print(mensaje)
				return render(request, "libr/index.html", {"mensaje": mensaje})
		else:
			return HttpResponse('Algún campo está vacío. Por favor revise de nuevo.')
		return render(request, "libr/inventario.html")

#Trae los datos del sitio, los retorna en formato json y guarda dentro de la sesión
@csrf_exempt
def buscar_js(request):
	if request.method == "POST":
		body = json.loads(request.body)
		isbn = body.get("SearchISBN")
		print(isbn)
		headers = {"User-Agent": "copodenieve9001@gmail.com"}
		url = f"https://openlibrary.org/search.json?isbn={isbn}"
		try:
			resp = requests.get(url, headers)
			data = resp.json()
			print(data)
			resultados = []
			for doc in data.get("docs", []):
				resultados.append({
				"titulo": doc.get("title", "no encontrado"),
				"autor": " ,".join(doc.get("author_name", [])),
				"año": doc.get("first_publish_year", "N/A"),
				"isbn": isbn,
				"link": f"https://openlibrary.org{doc.get('key')}" if doc.get('key') else "N/A"}
			)
                
			request.session["resultados"] = resultados
			print(resultados)
			if resultados:
				return JsonResponse({ "resultados": resultados, "exito":True })
			else:
				return JsonResponse({"mensaje": "No resultados para esta búsqueda.", "exito":False})
		except Exception as e:
			return JsonResponse({"error": str(e)}, status=500)

@login_required
@csrf_exempt
def modificar(request, id):
	if id > 0:
		libro = Libro.objects.get(id=id)
		mensaje = ""
		if request.method in ["POST", "PUT"]:
			try:
				data = json.loads(request.body)
				libro.titulo = data.get("titulo", libro.titulo)
				libro.autor = data.get("autor", libro.autor)
				libro.link = data.get("link", libro.link)
				campos = ["año", "cantidad", "estante", "isbn", "estanteria"]
				if all(data.get(campo) not in [None, ''] for campo in campos):
					libro.año = data.get("año", libro.año)
					libro.cantidad = data.get("cantidad", libro.cantidad)
					libro.isbn = data.get("isbn", libro.isbn)
			
					libro.estante = data.get("estante", libro.estante)
					libro.estanteria = data.get("estanteria", libro.estanteria)
				else:
					return render(request, "libr/modificar.html" ,{"libro": libro, "mensaje": "Un campo está vacío."})
				try:
					libro.save()
					return JsonResponse({"mensaje": "Actualización realizada correctamente."})
					mensaje = "Actualización realizada correctamente."
				except Exception as e:
					mensaje = "Un campo está vacío."
					return JsonResponse({"error": str(e)})
			except Exception as e:
				mensaje = "Un campo está vacío."
				return JsonResponse({"error": str(e)})
	return render(request, "libr/modificar.html",{"libro": libro, "mensaje": mensaje})

@login_required
def agregar_manualmente(request):
	mensaje = None
	if request.method == "POST":
		titulo = request.POST.get("titulo")
		autor = request.POST.get("autor")
		año = request.POST.get("año")
		isbn = request.POST.get("isbn")
		link = request.POST.get("link")
		cantidad = request.POST.get("cantidad")
		estante = request.POST.get("estante")
		estanteria = request.POST.get("estanteria")
		try:
			Libro.objects.create(titulo=titulo, autor=autor, isbn=isbn, año=año, link=link, cantidad=cantidad, estante=estante, estanteria=estanteria)
			mensaje = "Libro agregado exitosamente."
		except Exception as e:
			mensaje = "Algún campo está vacío o es muy largo."
	return render(request, "libr/agregar.html", {"mensaje": mensaje})

@login_required
def eliminar(request, id):
	mensaje = ""
	libro = Libro.objects.get(id=id)
	if libro:
		try:
			libro.delete()
			mensaje = "Libro eliminado exitosamente."
		except Exception as e:
			mensaje = "Libro no encontrado."
	return redirect('inventario')

@login_required
def eliminar_usuario(request, codigo):
	alumno = Estudiante.objects.filter(codigo_barras=codigo).first()
	profe = Maestro.objects.filter(codigo_barras=codigo).first()
	usuario = alumno or profe
	mensaje = None
	if usuario:
		try:
			usuario.delete()
			mensaje = "Usuario eliminado exitosamente."
		except Exception as e:
			mensaje = "Usuario no encontrado."
	return redirect('administrar_perfiles')

#Realiza el prestamo. Si es un maestro, es redireccionado a otro para llenar el campo de cantidad.
@login_required
@csrf_exempt
def prestar_view(request):
	mensaje = None
	if request.method == "POST":
		try:
			libro = request.POST.get("codigo_libro")
			libroBD = Libro.objects.filter(isbn=libro).first()
			user = request.POST.get("codigo_usuario")
			alumno = Estudiante.objects.filter(codigo_barras=user).first()
			profe = Maestro.objects.filter(codigo_barras=user).first()
			usuario = alumno or profe
			if libroBD and alumno:
				try:
					libroBD = Libro.objects.get(isbn=libro)
					Prestamo.objects.create(usuario=usuario, libro=libroBD)
					mensaje = "Prestamo realizado con éxito."
				except Exception as e:
					print(e)
					mensaje = f"Error al asignar un préstamo. Por favor intente de nuevo. Error: {e}"
			elif libroBD and profe:
				return redirect('prestamo_maestro', codigo_libro=libro, codigo_maestro=user)
		except Exception as e:
			mensaje = f"Oops. Hubo un error. Error: {e}"
	return render(request, "libr/prestamos_menu.html", {"mensaje": mensaje, "es_profe":False})


def ver_prestamos(request, codigo):
	prestamos = None
	elementos = []
	try:
		profe = Maestro.objects.filter(codigo_barras=codigo).first()
		alumno = Estudiante.objects.filter(codigo_barras=codigo).first()
		user = profe or alumno
		if profe:
			prestamos = Prestamo_Maestro.objects.filter(maestro=profe)
			for prestamo in prestamos:
				elementos.append({"tipo": "maestro", "obj":prestamo})
		elif alumno:
			prestamos = Prestamo.objects.filter(usuario=alumno)
			for prestamo in prestamos:
				elementos.append({"tipo": "alumno", "obj":prestamo})
	except Exception as e:
		print(e)
		messages.error(f"Error: {e}")
	return render(request, "libr/libros_prestados.html", {"prestamos": elementos})


@login_required
def prestamo_maestro(request, codigo_libro, codigo_maestro):
	libro = Libro.objects.filter(isbn=codigo_libro).first()
	profe = Maestro.objects.filter(codigo_barras=codigo_maestro).first()
	mensaje = None
	if request.method == "POST":
		libro1 = request.POST.get("codigo_libro")
		libroDB = Libro.objects.filter(isbn=libro1).first()
		user = request.POST.get("codigo_usuario")
		profe = Maestro.objects.filter(codigo_barras=user).first()
		cantidad = request.POST.get("cantidad")
		try:
			cantidad = int(cantidad)
		except Exception as e:
			mensaje = "Valor no númerico."
		if libroDB and profe and cantidad:
			if cantidad <= libroDB.cantidad:
				try:
					Prestamo_Maestro.objects.create(libro=libroDB, maestro=profe, cantidad=cantidad)
					mensaje = "Prestamo realizado con exito."
				except Exception as e:
					mensaje = f"Hubo un error inesperado: {e}"
			else:
				mensaje = "La cantidad es mayor a la registrada en el inventario."
		else:
			mensaje = "Uno de los campos está vacío."
	return render(request, "libr/prestamos_menu.html", {"es_profe": True, "profe": profe, "libro": libro, "mensaje":mensaje})


#Generera el pdf del inventario.
def generar_pdf(request):
	response = HttpResponse(content_type="application/pdf")
	response['Content-Disposition'] = 'attachment; filename="inventario.pdf"'
	doc = SimpleDocTemplate(response, pagesize=letter)
	elementos = []
	libros = Libro.objects.all()
	styles = getSampleStyleSheet()
	style = styles["Normal"]
	data = [["ID", "ISBN" ,"Título", "Autor", "Cantidad", "N. Estante", "N. Estantería"]]
	for libro in libros:
		data.append([libro.id, libro.isbn, Paragraph(libro.titulo, style), Paragraph(libro.autor, style), libro.cantidad, libro.estante, libro.estanteria])
	tabla = Table(data, colWidths=[40,90,120,120,60,80,90], repeatRows=1)
	tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
	elementos.append(tabla)
	doc.build(elementos)
	return response

#Filtra los libros por nombre, autor o isbn.
def buscar(request):
	if request.method == "POST":	
		str = request.POST.get("query")
		libro = Libro.objects.filter(Q(autor__icontains=str)| Q(titulo__icontains=str) | Q(isbn__icontains=str))
		if libro.exists():
			return render(request, "libr/inventario.html", {"libros": libro})
		else:
			return render(request, "libr/inventario.html", {"mensaje": "No fue encontrado."})
	return render(request, "libr/inventario.html")

@login_required
def opciones_perfiles_view(request):
	return render(request, "libr/opciones.html")

@login_required
def agregar_perfil(request, id):
	mensaje = None
	if id == 1:
		if request.method == "POST":
			nombre = request.POST.get("nombre")
			grado = request.POST.get("grado")
			seccion = request.POST.get("seccion")
			if nombre and grado and seccion:
				isbn = codes.generar_EAN()
				while Estudiante.objects.filter(codigo_barras=isbn).exists():
					isbn = codes.generar_EAN()
				img = codes.generar_barcode1(isbn, nombre)
				try:
					Estudiante.objects.create(nombre=nombre, grado=grado, seccion=seccion, codigo_img=img, codigo_barras=isbn)
					est = Estudiante.objects.get(codigo_barras=isbn)
					mensaje = "Perfil agregado exitosamente." 
					return redirect('generar_est_pdf', codigo=isbn)
				except Exception as e:
					mensaje = "Algún campo está vacío o es muy largo."
			else: 
				mensaje = "El campo está vacío."
		form = forms.PresetGrados
		return render(request, "libr/perfil.html", {"grados": form, "id": id, "mensaje": mensaje})
	elif id == 2:
		if request.method == "POST":
			nombre = request.POST.get("nombre")
			if nombre:
				cb = codes.generar_EAN()
				while Maestro.objects.filter(codigo_barras=cb).exists():
					cb = codes.generar_EAN()
				img = codes.generar_barcode1(cb, nombre)
				try:
					Maestro.objects.create(nombre=nombre, codigo_img=img, codigo_barras=cb)
					profe = Maestro.objects.get(codigo_barras=cb)
					mensaje = "Perfil agregado exitosamente."
					return redirect('generar_est_pdf', codigo=cb)
				except Exception as e:
					mensaje = "Algún campo está vacío o es muy largo."
			else:
				mensaje = "El campo está vacío."
		return render(request, "libr/perfil.html", {"id": id, "mensaje": mensaje})

#Muestra a todos los pefiles
def admin_view(request):
	estudiantes = Estudiante.objects.all()
	profesores = Maestro.objects.all()
	elementos = []
	for maestro in profesores:
		elementos.append(maestro)
	for alumno in estudiantes:
		elementos.append(alumno)
	paginator = Paginator(elementos, 20)
	num_pag = request.GET.get("page")
	page_obj = paginator.get_page(num_pag)
	return render(request, "libr/admin.html", {"page_obj": page_obj})


#Genera el pdf del usuario/perfil y lo guarda como path a la base de datos
def generar_est_pdf(request, codigo):
	est = Estudiante.objects.filter(codigo_barras=codigo)
	profe = Maestro.objects.filter(codigo_barras=codigo)
	if est.exists():
		est = Estudiante.objects.get(codigo_barras=codigo)
		try:
			buffer = BytesIO()
			canva = canvas.Canvas(buffer, pagesize=letter)
			canva.drawString(50,200, f"Nombre: { est.nombre }")
			canva.drawString(50,210, f"Grado: { est.grado }")
			canva.drawString(50, 220, f"Sección: { est.seccion.upper() }")
			if est.codigo_img:
				canva.drawImage(est.codigo_img.path, 50, 300, width=500, height=200)
			canva.showPage()
			canva.save()
			buffer.seek(0)
			pdf = ContentFile(buffer.read())
			filename = slugify(est.nombre)+".pdf"
			est.pdf.save(filename, pdf)
			response = HttpResponse(pdf, content_type="application/pdf")
			response['Content-Disposition'] = f'attachment; filename="{filename}"'
			return response
		except Exception as e:
			return messages.error(request, f"Error en la creación del pdf. Error: {e}")
	elif profe.exists():
		profe = Maestro.objects.get(codigo_barras=codigo)
		try:
			buffer = BytesIO()
			canva = canvas.Canvas(buffer, pagesize=letter)
			canva.drawString(50, 200, f"Nombre: { profe.nombre }")
			if profe.codigo_img:
				canva.drawImage(profe.codigo_img.path, 50, 280, width=500, height=200)
			canva.showPage()
			canva.save()
			buffer.seek(0)
			pdf = ContentFile(buffer.read())
			filename = slugify(profe.nombre)+".pdf"
			profe.pdf.save(filename, pdf)
			response = HttpResponse(pdf, content_type="application/pdf")
			response['Content-Disposition'] = f'attachment; filename="{filename}"'
			return response
		except Exception as e:
			return messages.error(request, f"Error en la creación del pdf. Error: {e}")


@login_required
def gestionar_perfil(request, codigo):
	alumno = Estudiante.objects.filter(codigo_barras=codigo)
	profe = Maestro.objects.filter(codigo_barras=codigo)
	if alumno.exists():
		usuario = Estudiante.objects.get(codigo_barras=codigo)
	elif profe.exists():
		usuario = Maestro.objects.get(codigo_barras=codigo)
	return render(request, "libr/gestionar.html", {"usuario": usuario})


@login_required
@csrf_exempt
def modificar_perfiles(request, codigo):
	est = Estudiante.objects.filter(codigo_barras=codigo)
	profe = Maestro.objects.filter(codigo_barras=codigo)
	form = None
	if est.exists():
		usuario = Estudiante.objects.get(codigo_barras=codigo)
		form = forms.PresetGrados(instance=usuario)
		if form.is_valid():
			form.save()
	elif profe.exists():
		usuario = Maestro.objects.get(codigo_barras=codigo)
	if request.method == "POST" and est.exists():
		
		nombre = request.POST.get("nombre")
		grado = request.POST.get("grado")
		seccion = request.POST.get("seccion")
		if nombre and grado and seccion:
			try:
				usuario.nombre = nombre
				usuario.grado = grado
				usuario.seccion = seccion
			
				usuario.save()
				return redirect('administrar_perfiles')
			except Exception as e:
				messages.error(request, f"Error: {e}")
		else:
			messages.error(request, "Hay algún campo vacío.")
	elif request.method == "POST" and profe.exists():
		nombre = request.POST.get("nombre")
		if nombre:
			try:
				usuario.nombre = nombre
				usuario.save()
				return redirect('administrar_perfiles')
			except Exception as e:
				messages.error(request, f"Error: {e}")
		else:
			messages.error(request, "Un campo está vacío.")
	return render(request, "libr/mod_user.html", {"usuario": usuario, "grados": form})


@login_required
def mostrar_pdf(request, codigo):
	alumno = Estudiante.objects.filter(codigo_barras=codigo).first()
	maestro = Maestro.objects.filter(codigo_barras=codigo).first()
	usuario = alumno or maestro
	print(usuario)
	if usuario and usuario.pdf:
		response = FileResponse(usuario.pdf.open('rb'), content_type="application/pdf")
		response["Content-Disposition"] = f"attachment; filename={ usuario.nombre }.pdf"
		return response

	return HttpResponse('<div class="mensaje">Algo salió mal...</div>')


def prestamos_view(request):
	print("here")
	estado = request.GET.get("estado")
	p = Prestamo.objects.all()
	p2 = Prestamo_Maestro.objects.all()
	elementos = []
	if estado == "pendientes":
		print("pendientes")
		p = p.filter(devuelto=False)
		p2 = p2.filter(devuelto=False)
	elif estado == "devueltos":
		print("devuelto")
		p = p.filter(devuelto=True)
		p2 = p2.filter(devuelto=True)
	for a in p:
		elementos.append({"tipo": "alumno", "obj": a})

	for s in p2:
		elementos.append({"tipo": "maestro", "obj": s})
	p = Paginator(elementos, 10)
	page = request.GET.get("page")
	elementos = p.get_page(page)
	return render(request, "libr/prestamos.html", {"prestamos": elementos})

@login_required
def devolver(request,tipo, id):
	p = None
	if tipo == "alumno":
		p = Prestamo.objects.get(id=id)
	elif tipo == "maestro":
		p = Prestamo_Maestro.objects.get(id=id)
	try:
		p.devuelto = True
		p.save()
		print(p.devuelto)
	except Exception as e:
		print(e)
	return redirect('prestamos_view')

@login_required
@csrf_exempt
def borrar_historial(request):
	try:
		p1 = Prestamo.objects.all().delete()
		p2 = Prestamo_Maestro.objects.all().delete()
		messages.success(request, "Historial borrado correctamente.")
	except Exception as e:
		print(e)
	return redirect('prestamos_view')

from django.db import models
from django import forms
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.
class User(AbstractUser):
        groups = models.ManyToManyField(Group, related_name="gro", blank=True)
        user_permissions = models.ManyToManyField(Permission, related_name="k", blank=True)
        def __str__(self):
                return f"User: {self.username} with password {self.password}"


class Libro(models.Model):
	titulo = models.CharField(max_length=100)
	autor = models.CharField(max_length=30)
	isbn = models.CharField(max_length=100)
	año = models.IntegerField(blank=True, null=True)
	link = models.CharField(max_length=150)
	cantidad = models.IntegerField()
	estante = models.IntegerField(null=True, blank=True)
	estanteria = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.titulo + " " + f"de " + self.autor

class Maestro(models.Model):
	nombre = models.CharField(max_length=100)
	codigo_barras = models.CharField(max_length=100)
	codigo_img = models.ImageField(upload_to="codigos/", null=True, blank=True)
	pdf = models.FileField(upload_to="fichas/", null=True, blank=True)

class Estudiante(models.Model):
	nombre = models.CharField(max_length=100)
	grados = [("kinder", "Kinder"), ("preparatoria","Preparatoria"), ("primero primaria","Primero Primaria"), ("segundo primaria","Segundo Primaria"),
	("tercero primaria", "Tercero Primaria"), ("cuarto primaria", "Cuarto Primaria"), ("quinto primaria", "Quinto Primaria"), 
	("sexto primaria", "Sexto Primaria"), ("primero básico", "Primero Básico"), ("segundo básico", "Segundo Básico"),
	("tercero básico", "Tercero Básico"), ("cuarto bachillerato en ciencias y letras", "Cuarto Bachillerato en Ciencias y Letras"),
	("cuarto bachillerato en computación", "Cuarto Bachillerato en Computación"),
	("quinto bachillerato en ciencias y letras", "Quinto Bachillerato en Ciencias y Letras"), 
	("quinto bachillerato en computación","Quinto Bachillerato en Computación")]
	secciones = [("a", "A"),("b", "B")]
	grado = models.CharField(max_length=50, choices=grados)
	seccion = models.CharField(max_length=1, choices=secciones)
	codigo_barras = models.CharField(max_length=100)
	codigo_img = models.ImageField(upload_to="codigos/", null=True, blank=True)
	pdf = models.FileField(upload_to="fichas/", null=True, blank=True)

	def __str__(self):
		return self.nombre 

class Prestamo(models.Model):
	usuario = models.ForeignKey(Estudiante, on_delete=models.CASCADE, name="usuario")
	libro = models.ForeignKey(Libro, on_delete=models.CASCADE, name="libro")
	fecha_prestamo = models.DateTimeField(default = timezone.now)
	devuelto = models.BooleanField(default=False)

class Prestamo_Maestro(models.Model):
	maestro = models.ForeignKey(Maestro, on_delete=models.CASCADE, name="maestro")
	libro = models.ForeignKey(Libro, on_delete=models.CASCADE, name="libro")
	cantidad = models.IntegerField(default=1)
	devuelto = models.BooleanField(default=False)
	fecha_prestamo = models.DateTimeField(default = timezone.now)

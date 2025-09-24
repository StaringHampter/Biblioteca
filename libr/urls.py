from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', views.index, name='index'),
	path('logout/', views.logout_view, name='logout'),
	path('login/', auth_views.LoginView.as_view(template_name='libr/login.html'), name='login'),
	path('password_reset/', auth_views.PasswordResetView.as_view(
            template_name='libr/password_reset_form.html'), name="password_reset"),
	path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='libr/password_reset_done.html'),
         name='password_reset_done'),
	path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='libr/password_reset_confirm.html'),
         name='password_reset_confirm'),
	path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='libr/password_reset_complete.html'),
         name='password_reset_complete'),
	path('buscar_libro/', views.buscar_libro, name='buscar_libro'),
	path('libros/', views.inventario, name='libros'),
	path('agregar_libros/', views.agregar_libro, name='agregar_libros'),
	path('confirmar_libro/<int:index>/', views.confirmar_libro, name='confirmar_libro'),
	path('agregarBaseDatos/', views.agregarBaseDatos, name='agregarBaseDatos'),
	path('buscar_js/', views.buscar_js, name='buscar_js'),
	path('inventario/', views.inventario, name='inventario'),
	path('modificar/<int:id>/', views.modificar, name='modificar'),
	path('agregar_manualmente/', views.agregar_manualmente, name='agregar_manualmente'),
	path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
	path('generar_pdf/', views.generar_pdf, name='generar_pdf'),
	path('buscar/', views.buscar, name='buscar'),
	path('crear_perfil/<int:id>/', views.agregar_perfil, name='crear_perfil'),
	path('administrar_perfiles/', views.admin_view, name='administrar_perfiles'),
	path('generar_est_pdf/<str:codigo>/', views.generar_est_pdf, name='generar_est_pdf'),
	path('gestionar_perfil/<str:codigo>/', views.gestionar_perfil, name='gestionar_perfil'),
	path('opciones_perfiles_view/', views.opciones_perfiles_view, name='opciones_perfiles_view'),
	path('modificar_perfiles/<str:codigo>/', views.modificar_perfiles, name='modificar_perfiles'),
	path('mostrar_pdf/<str:codigo>/', views.mostrar_pdf, name='mostrar_pdf'),
	path('eliminar_usuario/<str:codigo>/', views.eliminar_usuario, name='eliminar_usuario'),
	path('prestar_view/', views.prestar_view, name='prestar_view'),
	path('prestamo_maestro/<str:codigo_libro>/<str:codigo_maestro>/', views.prestamo_maestro, name='prestamo_maestro'),
	path('prestamos_view/', views.prestamos_view, name='prestamos_view'),
	path('devolver/<str:tipo>/<int:id>/', views.devolver, name='devolver'),
	path('borrar_historial/', views.borrar_historial, name='borrar_historial'),
	path('ver_prestamos/<str:codigo>/', views.ver_prestamos, name='ver_prestamos'),
	path('buscar_usuario/', views.buscar_usuario, name='buscar_usuario')
]

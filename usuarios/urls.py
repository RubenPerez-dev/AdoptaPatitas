from django.contrib.auth import views as auth_views
from django.urls import path

from usuarios import views
from usuarios.forms import LoginForm

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.RegistroAdoptanteView.as_view(), name='registro'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='usuarios/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path(
        'zona-autenticada/',
        views.ZonaAutenticadaView.as_view(),
        name='zona_autenticada',
    ),
]

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from usuarios.forms import PerfilAdoptanteForm, RegistroUsuarioForm
from usuarios.models import RolUsuario


class RegistroAdoptanteView(View):
    """Registro público de adoptantes.

    Crea Usuario + PerfilAdoptante en una única operación atómica. El rol
    se fuerza siempre a RolUsuario.ADOPTANTE en esta vista, sin depender
    de ningún valor recibido por POST: el formulario ni siquiera expone
    ese campo (ver usuarios/forms.py), pero además el backend nunca lo lee
    de la petición, evitando cualquier intento de escalada de privilegios
    (rol=trabajador, rol=administrador, is_staff=True, is_superuser=True).
    """

    template_name = 'usuarios/registro.html'

    def get(self, request):
        contexto = {
            'usuario_form': RegistroUsuarioForm(),
            'perfil_form': PerfilAdoptanteForm(),
        }
        return render(request, self.template_name, contexto)

    def post(self, request):
        usuario_form = RegistroUsuarioForm(request.POST)
        perfil_form = PerfilAdoptanteForm(request.POST)

        if usuario_form.is_valid() and perfil_form.is_valid():
            with transaction.atomic():
                # save(commit=False) para poder fijar el rol antes de
                # guardar en base de datos, ignorando cualquier valor que
                # pudiera llegar en request.POST para 'rol' (el formulario
                # no lo expone, pero se refuerza aquí explícitamente).
                usuario = usuario_form.save(commit=False)
                usuario.rol = RolUsuario.ADOPTANTE
                usuario.is_staff = False
                usuario.is_superuser = False
                usuario.save()

                perfil = perfil_form.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

            messages.success(
                request,
                'Registro completado correctamente. Ya puedes iniciar sesión.',
            )
            return redirect('usuarios:login')

        contexto = {
            'usuario_form': usuario_form,
            'perfil_form': perfil_form,
        }
        return render(request, self.template_name, contexto)


class ZonaAutenticadaView(LoginRequiredMixin, TemplateView):
    """Página mínima que solo pueden ver usuarios autenticados.

    LoginRequiredMixin comprueba la autenticación en el backend (no
    depende de ocultar enlaces en el frontend): si el usuario no está
    autenticado, Django le redirige a LOGIN_URL automáticamente.
    """

    template_name = 'usuarios/zona_autenticada.html'
    login_url = reverse_lazy('usuarios:login')

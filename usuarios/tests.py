from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from usuarios.models import (
    Experiencia,
    PerfilAdoptante,
    RolUsuario,
    TiempoDisponible,
    TipoVivienda,
    Usuario,
)


class UsuarioModelTests(TestCase):
    """Tests del modelo Usuario."""

    def test_crear_usuario_correctamente(self):
        usuario = Usuario.objects.create_user(
            username='adoptante1',
            password='contrasena-segura-123',
        )
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(usuario.username, 'adoptante1')

    def test_rol_por_defecto_es_adoptante(self):
        usuario = Usuario.objects.create_user(
            username='adoptante2',
            password='contrasena-segura-123',
        )
        self.assertEqual(usuario.rol, RolUsuario.ADOPTANTE)

    def test_los_tres_roles_definidos_existen(self):
        valores_esperados = {'adoptante', 'trabajador', 'administrador'}
        valores_reales = {choice.value for choice in RolUsuario}
        self.assertEqual(valores_reales, valores_esperados)

    def test_telefono_puede_quedar_vacio(self):
        usuario = Usuario.objects.create_user(
            username='adoptante3',
            password='contrasena-segura-123',
        )
        self.assertEqual(usuario.telefono, '')

    def test_se_puede_asignar_rol_trabajador(self):
        usuario = Usuario.objects.create_user(
            username='trabajador1',
            password='contrasena-segura-123',
            rol=RolUsuario.TRABAJADOR,
        )
        self.assertEqual(usuario.rol, RolUsuario.TRABAJADOR)

    def test_contrasena_no_se_guarda_en_texto_plano(self):
        usuario = Usuario.objects.create_user(
            username='adoptante4',
            password='contrasena-segura-123',
        )
        # Django siempre hashea la contraseña; nunca debe coincidir con el
        # valor original en texto plano almacenado en la base de datos.
        self.assertNotEqual(usuario.password, 'contrasena-segura-123')
        self.assertTrue(usuario.check_password('contrasena-segura-123'))


class PerfilAdoptanteModelTests(TestCase):
    """Tests del modelo PerfilAdoptante y su relación con Usuario."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='adoptante_perfil',
            password='contrasena-segura-123',
        )

    def test_perfil_se_relaciona_uno_a_uno_con_usuario(self):
        perfil = PerfilAdoptante.objects.create(usuario=self.usuario)
        self.assertEqual(perfil.usuario, self.usuario)
        self.assertEqual(self.usuario.perfil_adoptante, perfil)

    def test_un_usuario_no_puede_tener_dos_perfiles(self):
        PerfilAdoptante.objects.create(usuario=self.usuario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PerfilAdoptante.objects.create(usuario=self.usuario)

    def test_valores_choices_tipo_vivienda(self):
        valores_esperados = {'piso', 'casa_con_jardin', 'casa_sin_jardin'}
        valores_reales = {choice.value for choice in TipoVivienda}
        self.assertEqual(valores_reales, valores_esperados)

    def test_valores_choices_experiencia(self):
        valores_esperados = {'ninguna', 'poca', 'moderada', 'alta'}
        valores_reales = {choice.value for choice in Experiencia}
        self.assertEqual(valores_reales, valores_esperados)

    def test_valores_choices_tiempo_disponible(self):
        valores_esperados = {'poco', 'moderado', 'mucho'}
        valores_reales = {choice.value for choice in TiempoDisponible}
        self.assertEqual(valores_reales, valores_esperados)

    def test_valores_por_defecto_del_perfil(self):
        perfil = PerfilAdoptante.objects.create(usuario=self.usuario)
        self.assertEqual(perfil.tipo_vivienda, TipoVivienda.PISO)
        self.assertFalse(perfil.tiene_ninos)
        self.assertFalse(perfil.tiene_otros_animales)
        self.assertEqual(perfil.experiencia_con_mascotas, Experiencia.NINGUNA)
        self.assertEqual(perfil.tiempo_disponible, TiempoDisponible.MODERADO)


def datos_registro_validos(**overrides):
    """Datos de POST válidos para el formulario de registro completo."""
    datos = {
        'username': 'nuevoadoptante',
        'email': 'nuevo@example.com',
        'first_name': 'Ana',
        'last_name': 'Pérez',
        'telefono': '600111222',
        'password1': 'ContrasenaSegura123!',
        'password2': 'ContrasenaSegura123!',
        'tipo_vivienda': TipoVivienda.CASA_CON_JARDIN,
        'experiencia_con_mascotas': Experiencia.MODERADA,
        'tiempo_disponible': TiempoDisponible.MUCHO,
        # tiene_ninos / tiene_otros_animales se omiten: checkboxes no
        # marcados equivalen a False.
    }
    datos.update(overrides)
    return datos


class RegistroViewTests(TestCase):
    """Tests del flujo de registro público de adoptantes (vista + forms)."""

    def setUp(self):
        self.client = Client()
        self.url_registro = reverse('usuarios:registro')

    def test_get_registro_devuelve_formulario(self):
        respuesta = self.client.get(self.url_registro)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('usuario_form', respuesta.context)
        self.assertIn('perfil_form', respuesta.context)

    def test_registro_correcto_crea_usuario_con_datos_esperados(self):
        respuesta = self.client.post(self.url_registro, datos_registro_validos())

        self.assertEqual(Usuario.objects.count(), 1)
        usuario = Usuario.objects.get(username='nuevoadoptante')

        self.assertEqual(usuario.email, 'nuevo@example.com')
        self.assertEqual(usuario.first_name, 'Ana')
        self.assertEqual(usuario.last_name, 'Pérez')
        self.assertEqual(usuario.telefono, '600111222')
        self.assertTrue(usuario.is_active)
        self.assertEqual(usuario.rol, RolUsuario.ADOPTANTE)

        # La contraseña nunca debe compararse en texto plano: se usa el
        # mecanismo de verificación de Django.
        self.assertNotEqual(usuario.password, 'ContrasenaSegura123!')
        self.assertTrue(usuario.check_password('ContrasenaSegura123!'))

        # Redirección tras registro correcto (a la página de login).
        self.assertRedirects(respuesta, reverse('usuarios:login'))

    def test_registro_correcto_crea_perfil_adoptante_con_datos_esperados(self):
        self.client.post(self.url_registro, datos_registro_validos())

        usuario = Usuario.objects.get(username='nuevoadoptante')
        self.assertTrue(PerfilAdoptante.objects.filter(usuario=usuario).exists())

        perfil = usuario.perfil_adoptante
        self.assertEqual(perfil.tipo_vivienda, TipoVivienda.CASA_CON_JARDIN)
        self.assertEqual(perfil.experiencia_con_mascotas, Experiencia.MODERADA)
        self.assertEqual(perfil.tiempo_disponible, TiempoDisponible.MUCHO)
        self.assertFalse(perfil.tiene_ninos)
        self.assertFalse(perfil.tiene_otros_animales)

    def test_registro_no_crea_usuario_si_falla_creacion_de_perfil(self):
        """La creación de Usuario + PerfilAdoptante debe ser atómica.

        Se simula un fallo al guardar el perfil (por ejemplo, un error
        inesperado de base de datos) y se comprueba que, gracias a
        transaction.atomic(), el Usuario tampoco queda creado: no debe
        quedar un usuario "huérfano" sin su perfil.
        """
        with patch(
            'usuarios.views.PerfilAdoptanteForm.save',
            side_effect=Exception('fallo simulado al guardar el perfil'),
        ):
            with self.assertRaises(Exception):
                self.client.post(self.url_registro, datos_registro_validos())

        self.assertEqual(Usuario.objects.count(), 0)
        self.assertEqual(PerfilAdoptante.objects.count(), 0)

    def test_registro_ignora_intento_de_asignar_rol_trabajador(self):
        datos = datos_registro_validos(rol='trabajador')
        self.client.post(self.url_registro, datos)

        usuario = Usuario.objects.get(username='nuevoadoptante')
        self.assertEqual(usuario.rol, RolUsuario.ADOPTANTE)

    def test_registro_ignora_intento_de_asignar_rol_administrador(self):
        datos = datos_registro_validos(rol='administrador')
        self.client.post(self.url_registro, datos)

        usuario = Usuario.objects.get(username='nuevoadoptante')
        self.assertEqual(usuario.rol, RolUsuario.ADOPTANTE)

    def test_registro_ignora_intento_de_activar_is_staff(self):
        datos = datos_registro_validos(is_staff=True)
        self.client.post(self.url_registro, datos)

        usuario = Usuario.objects.get(username='nuevoadoptante')
        self.assertFalse(usuario.is_staff)

    def test_registro_ignora_intento_de_activar_is_superuser(self):
        datos = datos_registro_validos(is_superuser=True)
        self.client.post(self.url_registro, datos)

        usuario = Usuario.objects.get(username='nuevoadoptante')
        self.assertFalse(usuario.is_superuser)

    def test_registro_username_duplicado_es_rechazado(self):
        Usuario.objects.create_user(
            username='nuevoadoptante',
            password='OtraContrasena123!',
        )
        respuesta = self.client.post(self.url_registro, datos_registro_validos())

        self.assertEqual(respuesta.status_code, 200)  # vuelve a mostrar el formulario
        self.assertEqual(Usuario.objects.count(), 1)  # no se crea un segundo usuario
        self.assertFormError(
            respuesta.context['usuario_form'],
            'username',
            'A user with that username already exists.',
        )

    def test_registro_contrasenas_no_coincidentes_es_rechazado(self):
        datos = datos_registro_validos(password2='OtraDistinta456!')
        respuesta = self.client.post(self.url_registro, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_registro_contrasena_demasiado_comun_es_rechazada(self):
        datos = datos_registro_validos(password1='password', password2='password')
        respuesta = self.client.post(self.url_registro, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_registro_campos_obligatorios_ausentes_es_rechazado(self):
        datos = datos_registro_validos()
        del datos['username']
        respuesta = self.client.post(self.url_registro, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_registro_email_invalido_es_rechazado(self):
        datos = datos_registro_validos(email='esto-no-es-un-email')
        respuesta = self.client.post(self.url_registro, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 0)


class LoginLogoutViewTests(TestCase):
    """Tests del flujo de login/logout mediante el sistema de Django."""

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='adoptante_login',
            password='ContrasenaSegura123!',
        )

    def test_login_credenciales_correctas(self):
        respuesta = self.client.post(reverse('usuarios:login'), {
            'username': 'adoptante_login',
            'password': 'ContrasenaSegura123!',
        })
        self.assertTrue(respuesta.wsgi_request.user.is_authenticated)

    def test_login_credenciales_incorrectas(self):
        respuesta = self.client.post(reverse('usuarios:login'), {
            'username': 'adoptante_login',
            'password': 'contrasena-equivocada',
        })
        self.assertFalse(respuesta.wsgi_request.user.is_authenticated)
        self.assertEqual(respuesta.status_code, 200)  # vuelve a mostrar el login

    def test_logout_cierra_la_sesion(self):
        self.client.login(username='adoptante_login', password='ContrasenaSegura123!')
        respuesta = self.client.post(reverse('usuarios:logout'))

        respuesta_zona = self.client.get(reverse('usuarios:zona_autenticada'))
        self.assertEqual(respuesta_zona.status_code, 302)  # ya no autenticado


class ZonaAutenticadaViewTests(TestCase):
    """Tests de la protección en backend de la zona autenticada mínima."""

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='adoptante_zona',
            password='ContrasenaSegura123!',
        )
        self.url_zona = reverse('usuarios:zona_autenticada')

    def test_usuario_no_autenticado_es_redirigido(self):
        respuesta = self.client.get(self.url_zona)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('usuarios:login'), respuesta.url)

    def test_usuario_autenticado_puede_acceder(self):
        self.client.login(username='adoptante_zona', password='ContrasenaSegura123!')
        respuesta = self.client.get(self.url_zona)
        self.assertEqual(respuesta.status_code, 200)

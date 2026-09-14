from django.db import IntegrityError, transaction
from django.test import TestCase

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

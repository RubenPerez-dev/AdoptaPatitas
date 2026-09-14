from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class RolUsuario(models.TextChoices):
    """Roles funcionales previstos para AdoptaPatitas.

    Este campo es independiente de is_staff / is_superuser: rol controla
    qué puede hacer el usuario dentro de la aplicación de negocio, mientras
    que is_staff / is_superuser controlan el acceso al panel de
    administración técnico de Django.
    """

    ADOPTANTE = 'adoptante', 'Adoptante'
    TRABAJADOR = 'trabajador', 'Trabajador'
    ADMINISTRADOR = 'administrador', 'Administrador'


class Usuario(AbstractUser):
    """Usuario personalizado de AdoptaPatitas.

    Extiende el usuario estándar de Django (AbstractUser) añadiendo el rol
    funcional del usuario y un teléfono de contacto. El resto de campos
    (username, password, email, first_name, last_name, is_staff,
    is_superuser, etc.) se heredan sin modificar.
    """

    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.ADOPTANTE,
        help_text='Rol funcional del usuario dentro de AdoptaPatitas.',
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text='Teléfono de contacto (opcional).',
    )

    def __str__(self):
        return self.username


class TipoVivienda(models.TextChoices):
    PISO = 'piso', 'Piso'
    CASA_CON_JARDIN = 'casa_con_jardin', 'Casa con jardín'
    CASA_SIN_JARDIN = 'casa_sin_jardin', 'Casa sin jardín'


class Experiencia(models.TextChoices):
    NINGUNA = 'ninguna', 'Ninguna'
    POCA = 'poca', 'Poca'
    MODERADA = 'moderada', 'Moderada'
    ALTA = 'alta', 'Alta'


class TiempoDisponible(models.TextChoices):
    POCO = 'poco', 'Poco'
    MODERADO = 'moderado', 'Moderado'
    MUCHO = 'mucho', 'Mucho'


class PerfilAdoptante(models.Model):
    """Información específica del adoptante.

    Se crea explícitamente (no mediante signals) durante el flujo de
    registro de un adoptante, en una fase posterior. Los datos aquí
    almacenados alimentarán el futuro sistema de recomendaciones.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_adoptante',
    )
    tipo_vivienda = models.CharField(
        max_length=20,
        choices=TipoVivienda.choices,
        default=TipoVivienda.PISO,
    )
    tiene_ninos = models.BooleanField(default=False)
    tiene_otros_animales = models.BooleanField(default=False)
    experiencia_con_mascotas = models.CharField(
        max_length=20,
        choices=Experiencia.choices,
        default=Experiencia.NINGUNA,
    )
    tiempo_disponible = models.CharField(
        max_length=20,
        choices=TiempoDisponible.choices,
        default=TiempoDisponible.MODERADO,
    )

    def __str__(self):
        return f'Perfil adoptante de {self.usuario.username}'

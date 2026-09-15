from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from usuarios.models import PerfilAdoptante, Usuario


def _aplicar_clases_bootstrap(form):
    """Añade las clases de Bootstrap adecuadas a cada tipo de campo."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault('class', 'form-check-input')
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault('class', 'form-select')
        else:
            widget.attrs.setdefault('class', 'form-control')


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro público de adoptantes.

    Extiende UserCreationForm (que ya gestiona la contraseña, su
    confirmación y los validadores estándar de Django) restringiendo
    explícitamente los campos visibles. El campo `rol` NUNCA se incluye
    aquí: el registro público siempre crea adoptantes, y esa regla se
    aplica en la vista (usuarios/views.py), no confiando en el formulario
    ni en el frontend.
    """

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Campos explícitos: nunca 'rol', 'is_staff' ni 'is_superuser'.
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_clases_bootstrap(self)


class PerfilAdoptanteForm(forms.ModelForm):
    """Datos específicos del adoptante recogidos durante el registro."""

    class Meta:
        model = PerfilAdoptante
        fields = [
            'tipo_vivienda',
            'tiene_ninos',
            'tiene_otros_animales',
            'experiencia_con_mascotas',
            'tiempo_disponible',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_clases_bootstrap(self)


class LoginForm(AuthenticationForm):
    """AuthenticationForm estándar de Django, solo con estilo Bootstrap.

    No cambia el comportamiento de autenticación: Django sigue
    verificando la contraseña y gestionando la sesión.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_clases_bootstrap(self)

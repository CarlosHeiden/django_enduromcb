from django import forms
from .models import Piloto, Categoria


class RegistrarLargadaForm(forms.Form):
    numero_piloto = forms.IntegerField(label='Número do Piloto')


class RegistrarChegadaForm(forms.Form):
    numero_piloto = forms.IntegerField(label='Número do Piloto')


class CadastrarPilotoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all())

    class Meta:
        model = Piloto
        fields = ['nome', 'numero_piloto', 'moto', 'categoria']

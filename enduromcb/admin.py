from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin
from .models import Categoria, Piloto, RegistrarLargada, RegistrarChegada, Resultados


@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    list_display = ['id', 'nome']
    search_fields = ['nome']


@admin.register(Piloto)
class PilotoAdmin(ImportExportModelAdmin):
    list_display = ['id', 'nome', 'numero_piloto', 'moto', 'categoria']
    search_fields = ['nome', 'numero_piloto']
    list_filter = ['categoria']


@admin.register(RegistrarLargada)
class RegistrarLargadaAdmin(ImportExportModelAdmin):
    list_display = ['id_volta', 'piloto', 'horario_largada']
    search_fields = ['piloto__nome', 'piloto__numero_piloto']


@admin.register(RegistrarChegada)
class RegistrarChegadaAdmin(ImportExportModelAdmin):
    list_display = ['id_volta', 'piloto', 'horario_chegada']
    search_fields = ['piloto__nome', 'piloto__numero_piloto']


@admin.register(Resultados)
class ResultadosAdmin(ImportExportModelAdmin):
    list_display = [
        'id', 'nome', 'numero_piloto', 'moto', 'categoria',
        'id_volta', 'horario_largada', 'horario_chegada',
        'tempo_volta', 'tempo_total'
    ]
    search_fields = ['nome', 'numero_piloto', 'categoria']

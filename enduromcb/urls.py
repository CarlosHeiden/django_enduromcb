from django.urls import path
from . import views


urlpatterns = [
   
    path('cadastrar_piloto/', views.cadastrar_piloto, name='cadastrar_piloto'),
    path(
        'registrar_largada/', views.registrar_largada, name='registrar_largada'
    ),
    path(
        'registrar_chegada/', views.registrar_chegada, name='registrar_chegada'
    ),
    path('resultados/', views.resultados, name='resultados'),
    path('resultado_piloto/',views.resultado_piloto, name='resultado_piloto'),
    path('exibir_pilotos/', views.exibir_pilotos, name='exibir_pilotos'),

    path('debug_totais/', views.debug_totais, name='debug_totais'),
    path('debug_tempos/', views.debug_tempos, name='debug_tempos'),

    
]
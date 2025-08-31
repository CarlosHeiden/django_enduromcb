from django.db import models
from datetime import timedelta


class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Piloto(models.Model):
    nome = models.CharField(max_length=100)
    numero_piloto = models.IntegerField(unique=True)
    moto = models.CharField(max_length=100, default='####', blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='pilotos')



class RegistrarLargada(models.Model):
    id_volta = models.AutoField(primary_key=True)
    piloto = models.ForeignKey(Piloto, on_delete=models.CASCADE, related_name='largadas')
    horario_largada = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'Largada: {self.piloto} - {self.horario_largada}'


class RegistrarChegada(models.Model):
    id_volta = models.AutoField(primary_key=True)
    piloto = models.ForeignKey(Piloto, on_delete=models.CASCADE, related_name='chegadas')
    horario_chegada = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'Chegada: {self.piloto} - {self.horario_chegada}'


class Resultados(models.Model):
    nome = models.CharField(max_length=100)
    numero_piloto = models.IntegerField()
    moto = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    id_volta = models.IntegerField()
    horario_largada = models.TimeField(null=True, blank=True)
    horario_chegada = models.TimeField(null=True, blank=True)
    tempo_volta = models.DurationField(null=True, blank=True)
    tempo_total = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome} ({self.numero_piloto})'
    

class OrdemLargada(models.Model):
    piloto = models.OneToOneField(
        Piloto,
        on_delete=models.CASCADE,
        related_name='ordem_largada',
        verbose_name="Piloto"
    )
    posicao = models.IntegerField(unique=True, verbose_name="Posição de Largada")

    class Meta:
        ordering = ['posicao']
        verbose_name = "Ordem de Largada"
        verbose_name_plural = "Ordens de Largada"

    def __str__(self):
        return f"Posição {self.posicao} - {self.piloto.numero_piloto} - {self.piloto.nome}" 


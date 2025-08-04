from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta, date
from django.http import HttpResponse
from .models import Piloto, RegistrarLargada, RegistrarChegada, Resultados, Categoria
from .forms import RegistrarLargadaForm, RegistrarChegadaForm, CadastrarPilotoForm
from .funcoes import formatar_timedelta_com_sinal


def cadastrar_piloto(request):
    if request.method == 'POST':
        form = CadastrarPilotoForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            numero_piloto = form.cleaned_data['numero_piloto']
            moto = form.cleaned_data['moto']
            categoria = form.cleaned_data['categoria']

            if Piloto.objects.filter(Q(nome=nome) | Q(numero_piloto=numero_piloto)).exists():
                messages.error(request, 'Já existe um piloto com esse nome ou número.')
            else:
                Piloto.objects.create(
                    nome=nome,
                    numero_piloto=numero_piloto,
                    moto=moto,
                    categoria=categoria
                )
                messages.success(request, 'Piloto cadastrado com sucesso.')
                return redirect('cadastrar_piloto')
    else:
        form = CadastrarPilotoForm()

    return render(request, 'cadastrar_piloto.html', {'form': form})


def registrar_largada(request):
    if request.method == 'POST':
        form = RegistrarLargadaForm(request.POST)
        if form.is_valid():
            numero_piloto = form.cleaned_data['numero_piloto']

            if not numero_piloto:
                messages.error(request, 'Número de piloto é obrigatório.')
                return redirect('registrar_largada')

            try:
                piloto = Piloto.objects.get(numero_piloto=numero_piloto)
            except Piloto.DoesNotExist:
                messages.error(request, 'Piloto não cadastrado.')
                return redirect('registrar_largada')

            agora = datetime.now().strftime('%H:%M:%S.%f')[:-3]

            RegistrarLargada.objects.create(
                piloto=piloto,
                horario_largada=agora
            )

            #messages.success(request, f'Largada registrada para piloto {piloto.numero_piloto}.')
            return redirect('registrar_largada')
    else:
        form = RegistrarLargadaForm()

    return render(request, 'registrar_largada.html', {'form': form})



def registrar_chegada(request):
    if request.method == 'POST':
        form = RegistrarChegadaForm(request.POST)
        if form.is_valid():
            numero_piloto = form.cleaned_data['numero_piloto']
            if not numero_piloto:
                messages.error(request, 'Número de piloto é obrigatório.')
                return redirect('registrar_chegada')

            try:
                piloto = Piloto.objects.get(numero_piloto=numero_piloto)
            except Piloto.DoesNotExist:
                messages.error(request, 'Piloto não cadastrado.')
                return redirect('registrar_chegada')


            agora = datetime.now().strftime('%H:%M:%S.%f')[:-3]

            RegistrarChegada.objects.create(
                piloto=piloto,
                horario_chegada=agora
            )

            save_dados_resultados(agora, piloto)
            return redirect('registrar_chegada')
    else:
        form = RegistrarChegadaForm()

    return render(request, 'registrar_chegada.html', {'form': form})


def save_dados_resultados(agora_str, piloto):
    chegada_time = datetime.strptime(agora_str, '%H:%M:%S.%f').time()

    largada = RegistrarLargada.objects.filter(piloto=piloto).last()
    if not largada or not largada.horario_largada:
        return

    horario_largada = largada.horario_largada

    # Cálculo correto do tempo de volta (real)
    tempo_volta_real = datetime.combine(date.today(), chegada_time) - datetime.combine(date.today(), horario_largada)

    # Soma dos tempos de voltas anteriores
    voltas_anteriores = Resultados.objects.filter(numero_piloto=piloto.numero_piloto).order_by('id_volta')

    tempo_total_final = sum(
        (v.tempo_volta for v in voltas_anteriores),
        timedelta(0)
    )

    # Registro completo da volta atual
    Resultados.objects.create(
        nome=piloto.nome,
        numero_piloto=piloto.numero_piloto,
        moto=piloto.moto,
        categoria=str(piloto.categoria),
        id_volta=largada.id_volta,
        horario_largada=horario_largada,
        horario_chegada=chegada_time,
        tempo_volta=tempo_volta_real,
        tempo_total=tempo_total_final + tempo_volta_real,
    )

def resultados(request):
    resultados_gerais = []

    for piloto in Piloto.objects.all():
        voltas = Resultados.objects.filter(numero_piloto=piloto.numero_piloto).order_by('id_volta')

        if voltas.count() <= 1:
            continue

        primeira_volta = voltas.first().tempo_volta

        total_pontos = 0
        for v in voltas[1:]:
            dif = v.tempo_volta - primeira_volta
            dif_ms = int(dif.total_seconds() * 1000)

            if dif_ms > 0:
                pontos = round(dif_ms / 1000)  # atrasado = 1 ponto por segundo
            elif dif_ms < 0:
                pontos = round(abs(dif_ms) / 1000) * 3  # adiantado = 3 pontos por segundo
            else:
                pontos = 0

            total_pontos += pontos

        resultados_gerais.append({
            'piloto': piloto,
            'numero_piloto': piloto.numero_piloto,
            'pontos_perdidos': total_pontos,
        })

    resultados_gerais.sort(key=lambda x: x['pontos_perdidos'])

    for pos, p in enumerate(resultados_gerais, start=1):
        p['position'] = pos

    return render(request, 'resultados.html', {'resultados_gerais': resultados_gerais})


def resultados_por_categorias(request):
    categorias = Categoria.objects.all()
    resultados_por_categoria = {cat: [] for cat in categorias}

    for categoria in categorias:
        pilotos_categoria = Piloto.objects.filter(categoria=categoria)

        for piloto in pilotos_categoria:
            voltas = Resultados.objects.filter(numero_piloto=piloto.numero_piloto).order_by('id_volta')

            if voltas.count() <= 1:
                continue

            tempo_total = sum(
                v.tempo_volta.total_seconds() for v in voltas[1:]
            )

            tempo_total_str = '{:02d}:{:02d}:{:02d}.{:03d}'.format(
                int(tempo_total // 3600),
                int((tempo_total % 3600) // 60),
                int(tempo_total % 60),
                int((tempo_total % 1) * 1000)
            )

            resultados_por_categoria[categoria].append({
                'nome': piloto.nome,
                'numero_piloto': piloto.numero_piloto,
                'tempo_total': tempo_total_str,
            })

        # ordena e adiciona posição
        resultados_por_categoria[categoria].sort(key=lambda x: x['tempo_total'])
        for pos, p in enumerate(resultados_por_categoria[categoria], start=1):
            p['position'] = pos

    return render(
        request,
        'resultados_por_categorias.html',
        {'resultados_por_categoria': resultados_por_categoria}
    )

from math import ceil

from datetime import timedelta
from django.shortcuts import render
from .models import Piloto, Resultados

def formatar_timedelta_com_sinal(td):
    total_ms = td.total_seconds() * 1000
    sinal = '+' if total_ms > 0 else '-' if total_ms < 0 else ''
    td_abs = abs(td)
    horas = int(td_abs.total_seconds() // 3600)
    minutos = int((td_abs.total_seconds() % 3600) // 60)
    segundos = int(td_abs.total_seconds() % 60)
    milissegundos = int((td_abs.total_seconds() % 1) * 1000)
    return f'{sinal}{horas:02d}:{minutos:02d}:{segundos:02d}.{milissegundos:03d}'

def resultado_piloto(request):
    piloto_detail = []

    for piloto in Piloto.objects.all():
        resultados = Resultados.objects.filter(numero_piloto=piloto.numero_piloto).order_by('id_volta')
        if not resultados.exists():
            continue

        primeira_volta = resultados.first().tempo_volta
        tempo_total_dif_ms = 0
        tempo_real_total = timedelta(0)
        total_pontos = 0
        volta_detail = []

        for res in resultados:
            tempo_volta = res.tempo_volta
            tempo_real_total += tempo_volta

            tempo_volta_str = '{:02d}:{:02d}:{:02d}.{:03d}'.format(
                int(tempo_volta.total_seconds() // 3600),
                int((tempo_volta.total_seconds() % 3600) // 60),
                int(tempo_volta.total_seconds() % 60),
                int((tempo_volta.total_seconds() % 1) * 1000)
            )

            dif = tempo_volta - primeira_volta
            if res != resultados.first():
                tempo_total_dif_ms += int(abs(dif.total_seconds()) * 1000)

            # Diferença formatada com sinal
            dif_volta1_str = formatar_timedelta_com_sinal(dif)

            # Status e Pontos
            status = ''
            pontos = 0
            if res != resultados.first():
                segundos_arredondado = round(abs(dif.total_seconds()))
                if dif.total_seconds() < 0:
                    status = 'adiantado'
                    pontos = segundos_arredondado * 3
                elif dif.total_seconds() > 0:
                    status = 'atrasado'
                    pontos = segundos_arredondado * 1
                total_pontos += pontos

            volta_detail.append({
                'id_volta': res.id_volta,
                'horario_largada': res.horario_largada.strftime('%H:%M:%S.%f')[:-3],
                'horario_chegada': res.horario_chegada.strftime('%H:%M:%S.%f')[:-3],
                'tempo_volta': tempo_volta_str,
                'dif_volta1_str': dif_volta1_str,
                'status': status,
                'pontos': pontos,
            })

        # Tempo total (baseado nas diferenças)
        total_dif = timedelta(milliseconds=tempo_total_dif_ms)
        tempo_total_str = '{:02d}:{:02d}:{:02d}.{:03d}'.format(
            int(total_dif.total_seconds() // 3600),
            int((total_dif.total_seconds() % 3600) // 60),
            int(total_dif.total_seconds() % 60),
            int((total_dif.total_seconds() % 1) * 1000)
        )

        # Tempo real total (critério de desempate)
        tempo_real_str = '{:02d}:{:02d}:{:02d}.{:03d}'.format(
            int(tempo_real_total.total_seconds() // 3600),
            int((tempo_real_total.total_seconds() % 3600) // 60),
            int(tempo_real_total.total_seconds() % 60),
            int((tempo_real_total.total_seconds() % 1) * 1000)
        )

        piloto_detail.append({
            'piloto': piloto,
            'numero_piloto': piloto.numero_piloto,
            'voltas': volta_detail,
            'tempo_total': tempo_total_str,
            'tempo_real': tempo_real_str,
            'total_pontos': total_pontos,
        })

    return render(request, 'resultado_piloto.html', {'piloto_detail': piloto_detail})

def exibir_pilotos(request):
    nome = request.GET.get('nome')
    numero_piloto = request.GET.get('numero_piloto')
    categoria = request.GET.get('categoria')
    if nome and numero_piloto and categoria:
        pilotos = Piloto.objects.filter(
            nome=nome, numero_piloto=numero_piloto, categoria=categoria
        )
    else:
        pilotos = Piloto.objects.all()
    return render(request, 'exibir_pilotos.html', {'pilotos': pilotos})

from django.http import HttpResponse
from django.utils.html import format_html

def debug_tempos(request):
    dados = []

    for resultado in Resultados.objects.all().order_by('numero_piloto', 'id_volta'):
        largada = resultado.horario_largada
        chegada = resultado.horario_chegada
        tempo_volta = resultado.tempo_volta

        def tempo_para_ms(t):
            return t.hour * 3600000 + t.minute * 60000 + t.second * 1000 + int(t.microsecond / 1000)

        if largada and chegada:
            largada_ms = tempo_para_ms(largada)
            chegada_ms = tempo_para_ms(chegada)
            calculado_ms = chegada_ms - largada_ms
        else:
            calculado_ms = None

        salvo_ms = int(tempo_volta.total_seconds() * 1000) if tempo_volta else None
        diferenca = (salvo_ms - calculado_ms) if calculado_ms is not None and salvo_ms is not None else None

        dados.append({
            'piloto': resultado.nome,
            'volta': resultado.id_volta,
            'largada': largada,
            'chegada': chegada,
            'salvo_ms': salvo_ms,
            'calculado_ms': calculado_ms,
            'diferenca': diferenca,
        })

    html = """
    <h2>Debug de Tempos</h2>
    <table border="1" cellpadding="6">
      <tr>
        <th>Piloto</th>
        <th>Volta</th>
        <th>Largada</th>
        <th>Chegada</th>
        <th>Tempo salvo (ms)</th>
        <th>Tempo calculado (ms)</th>
        <th>Diferença (ms)</th>
      </tr>
    """

    for item in dados:
        cor = ''
        if item['diferenca'] is not None and abs(item['diferenca']) > 5:
            cor = ' style="background-color:#fdd"'
        html += f"""
        <tr{cor}>
          <td>{item['piloto']}</td>
          <td>{item['volta']}</td>
          <td>{item['largada']}</td>
          <td>{item['chegada']}</td>
          <td>{item['salvo_ms']}</td>
          <td>{item['calculado_ms']}</td>
          <td>{item['diferenca']}</td>
        </tr>
        """

    html += "</table>"
    return HttpResponse(format_html(html))

from django.http import HttpResponse
from django.utils.html import format_html

def debug_totais(request):
    html = """
    <h2>Debug de Tempo Total</h2>
    <table border="1" cellpadding="6">
        <tr>
            <th>Piloto</th>
            <th>Voltas</th>
            <th>Soma diferenças (ms)</th>
            <th>Tempo real (ms)</th>
            <th>Diferença (ms)</th>
        </tr>
    """

    for piloto in Piloto.objects.all():
        voltas = Resultados.objects.filter(numero_piloto=piloto.numero_piloto).order_by('id_volta')

        if voltas.count() <= 1:
            continue

        tempo_primeira_volta = voltas.first().tempo_volta
        soma_diferencas = sum(abs(v.tempo_volta - tempo_primeira_volta).total_seconds() for v in voltas[1:])
        soma_diferencas_ms = int(soma_diferencas * 1000)

        largada2 = voltas[1].horario_largada
        chegada_final = voltas.last().horario_chegada

        tempo_real = (
            datetime.combine(date.today(), chegada_final) - datetime.combine(date.today(), largada2)
        ).total_seconds()
        tempo_real_ms = int(tempo_real * 1000)

        diferenca = soma_diferencas_ms - tempo_real_ms

        cor = ''
        if abs(diferenca) > 5:
            cor = ' style="background-color:#fdd"'

        html += f"""
        <tr{cor}>
            <td>{piloto.nome}</td>
            <td>{voltas.count()}</td>
            <td>{soma_diferencas_ms}</td>
            <td>{tempo_real_ms}</td>
            <td>{diferenca}</td>
        </tr>
        """

    html += "</table>"
    return HttpResponse(format_html(html))

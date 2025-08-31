from django.test import TestCase, Client
from django.urls import reverse
from .models import Piloto, Categoria

class CadastrarPilotoViewTest(TestCase):
    
    def setUp(self):
        """
        Configuração inicial para todos os testes.
        Cria um cliente de teste e uma categoria para uso.
        """
        self.client = Client()
        self.url = reverse('cadastrar_piloto')
        self.categoria_enduro = Categoria.objects.create(nome='Enduro')
    
    def test_cadastrar_piloto_sucesso(self):
        """
        Verifica se um novo piloto é cadastrado com sucesso.
        Espera um redirecionamento (status 302) e que o piloto seja salvo.
        """
        response = self.client.post(self.url, {
            'nome': 'Piloto Novo',
            'numero_piloto': 99,
            'moto': 'Honda CRF 250',
            'categoria': self.categoria_enduro.id,
        })
        
        # O teste verifica se o formulário foi salvo com sucesso.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Piloto.objects.count(), 1)
        self.assertRedirects(response, self.url)
        
    def test_cadastrar_piloto_duplicado_numero(self):
        """
        Verifica o cenário de erro quando o número do piloto já existe.
        Espera que a página seja renderizada novamente (status 200) com
        uma mensagem de erro na resposta.
        """
        # Cria um piloto já existente no banco de dados.
        Piloto.objects.create(
            nome='Piloto Existente',
            numero_piloto=542,
            moto='Honda',
            categoria=self.categoria_enduro
        )
        
        # Tenta cadastrar um novo piloto com o mesmo número, mas nome diferente.
        response = self.client.post(self.url, {
            'nome': 'Outro Piloto',
            'numero_piloto': 542, # Número duplicado
            'moto': 'Kawasaki',
            'categoria': self.categoria_enduro.id,
        })
        
        # Espera que o status seja 200, pois não houve redirecionamento.
        self.assertEqual(response.status_code, 200)
        
        # O teste agora procura pela mensagem de erro padrão do Django.
        self.assertContains(response, 'Piloto com este Numero piloto já existe.')
        
        # Garante que nenhum novo piloto foi criado no banco de dados.
        self.assertEqual(Piloto.objects.count(), 1)

    def test_cadastrar_piloto_duplicado_nome_permitido(self):
        """
        Verifica que é possível cadastrar um piloto com o mesmo nome,
        desde que o número seja único.
        """
        # Cria um piloto já existente com um nome comum.
        Piloto.objects.create(
            nome='Carlos',
            numero_piloto=542,
            moto='Honda',
            categoria=self.categoria_enduro
        )
        
        # Tenta cadastrar um novo piloto com o mesmo nome, mas número diferente.
        response = self.client.post(self.url, {
            'nome': 'Carlos', # Nome duplicado, mas permitido pela regra de negócio
            'numero_piloto': 15,
            'moto': 'Yamaha',
            'categoria': self.categoria_enduro.id,
        })
        
        # Espera que o cadastro seja bem-sucedido e haja um redirecionamento.
        self.assertEqual(response.status_code, 302)
        
        # Verifica se agora existem dois pilotos no banco de dados.
        self.assertEqual(Piloto.objects.count(), 2)
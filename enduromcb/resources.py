# seu_app/resources.py

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Piloto, OrdemLargada

class OrdemLargadaResource(resources.ModelResource):
    # O campo 'piloto' é uma chave estrangeira, então usamos um widget especial.
    # O campo 'numero_piloto' é o que o usuário vai fornecer no CSV.
    numero_piloto = fields.Field(
        column_name='numero_piloto',
        attribute='piloto',
        widget=ForeignKeyWidget(Piloto, 'numero_piloto')
    )

    class Meta:
        model = OrdemLargada
        # Campos que o django-import-export vai usar para importar/exportar.
        fields = ('posicao', 'numero_piloto')
        # Campos de identificação para evitar duplicatas.
        import_id_fields = ('posicao',)
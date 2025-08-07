from django import template

register = template.Library()

@register.filter
def format_timedelta_hms_ms(value):
    if not value:
        return ''
    total_seconds = value.total_seconds()
    horas = int(total_seconds // 3600)
    minutos = int((total_seconds % 3600) // 60)
    segundos = int(total_seconds % 60)
    milissegundos = int((total_seconds % 1) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}.{milissegundos:03d}"

from datetime import timedelta


def formatar_timedelta_com_sinal(dif: timedelta) -> str:
    total_ms = int(dif.total_seconds() * 1000)
    sinal = '+' if total_ms > 0 else '-' if total_ms < 0 else ''
    abs_total_ms = abs(total_ms)

    horas = abs_total_ms // 3600000
    minutos = (abs_total_ms % 3600000) // 60000
    segundos = (abs_total_ms % 60000) // 1000
    milissegundos = abs_total_ms % 1000

    return f"{sinal}{horas:02d}:{minutos:02d}:{segundos:02d}.{milissegundos:03d}"




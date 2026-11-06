from datetime import datetime, time

def identificar_turno_periodo():

    agora = datetime.now()

    # Domingo
    if agora.weekday() == 6:
        return "FORA DE PRODUÇÃO", "-"

    hora_atual = agora.time()

    # 1º TURNO
    if time(6,20) <= hora_atual <= time(11,15):
        return "1º TURNO", "1º PERÍODO"

    if time(12,16) <= hora_atual <= time(16,20):
        return "1º TURNO", "2º PERÍODO"

    # 2º TURNO
    if time(16,21) <= hora_atual <= time(20,40):
        return "2º TURNO", "1º PERÍODO"

    if time(21,41) <= hora_atual or hora_atual <= time(1,40):
        return "2º TURNO", "2º PERÍODO"

    # Intervalos
    if time(11,16) <= hora_atual <= time(12,15):
        return "ALMOÇO", "-"

    if time(20,41) <= hora_atual <= time(21,40):
        return "JANTA", "-"
    
    return "FORA DE PRODUÇÃO", "-"

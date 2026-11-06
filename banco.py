import sqlite3
from datetime import datetime

import os

BANCO = os.path.join(
    "database",
    "supervisorio.db"
)

def criar_banco():

    os.makedirs(
        "database",
        exist_ok=True
    )

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS eventos (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data_hora TEXT,

        estacao INTEGER,

        evento TEXT,

        turno TEXT,

        periodo TEXT,

        hora_inicio TEXT,

        hora_fim TEXT,

        duracao TEXT

    )

    """)

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS historico_turnos (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data TEXT,

        turno TEXT,

        total_paradas INTEGER,

        tempo_total TEXT,

        maior_parada TEXT,

        estacao_recorrente TEXT,

        estacao_impactante TEXT,

        disponibilidade TEXT

    )

    """)

    conexao.commit()

    conexao.close()


def registrar_evento(estacao, evento, turno, periodo):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()


    agora = datetime.now()


    cursor.execute(
        """
        INSERT INTO eventos
        (
        data_hora,
        estacao,
        evento,
        turno,
        periodo,
        hora_inicio
        )

        VALUES (?, ?, ?, ?, ?, ?)

        """,

        (
        agora.strftime("%d/%m/%Y %H:%M:%S"),
        estacao,
        evento,
        turno,
        periodo,
        agora.strftime("%Y-%m-%d %H:%M:%S")
        )

    )


    conexao.commit()
    conexao.close()




def listar_eventos():

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()


    cursor.execute("""
        SELECT 
        data_hora,
        estacao,
        evento,
        turno,
        periodo,
        duracao

        FROM eventos

        ORDER BY id DESC
    """)


    dados = cursor.fetchall()


    conexao.close()


    return dados

def contar_paradas(turno):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM eventos
        WHERE evento = 'EMERGENCIA_ACIONADA'
        AND turno = ?
    """, (turno,))

    resultado = cursor.fetchone()[0]

    conexao.close()

    return resultado

def finalizar_parada(estacao):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    agora = datetime.now()

    cursor.execute("""
        SELECT id, hora_inicio
        FROM eventos
        WHERE estacao = ?
        AND evento = 'EMERGENCIA_ACIONADA'
        AND hora_fim IS NULL

        ORDER BY id DESC
        LIMIT 1
    """, (estacao,))

    registro = cursor.fetchone()

    if registro:

        id_evento = registro[0]
        hora_inicio = registro[1]

        
        inicio = datetime.strptime(
            hora_inicio,
            "%Y-%m-%d %H:%M:%S"
        )

        tempo_total = int(
            (agora - inicio).total_seconds()
        )

        horas = tempo_total // 3600

        minutos = (tempo_total % 3600) // 60

        segundos = tempo_total % 60

        duracao = (
            f"{horas:02d}:"
            f"{minutos:02d}:"
            f"{segundos:02d}"
        )

        cursor.execute("""
            UPDATE eventos
            SET hora_fim = ?,
                duracao = ?
            WHERE id = ?
        """,
        (
            agora.strftime("%Y-%m-%d %H:%M:%S"),

            duracao,
            id_evento
        ))

    conexao.commit()
    conexao.close()

def emergencia_aberta(estacao):

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM eventos
        WHERE estacao = ?
        AND evento = 'EMERGENCIA_ACIONADA'
        AND hora_fim IS NULL
        LIMIT 1
    """, (estacao,))

    resultado = cursor.fetchone()

    conexao.close()

    return resultado is not None

def tempo_total_paradas(turno=None):
    
    atualizar_duracao_em_aberto()

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            AND turno = ?
        """, (turno,))

    else:

        cursor.execute("""
            SELECT duracao
            FROM eventos
            WHERE duracao IS NOT NULL
        """)

    registros = cursor.fetchall()

    conexao.close()

    total_segundos = 0

    for registro in registros:

        duracao = registro[0]

        if duracao:

            horas, minutos, segundos = map(
                int,
                duracao.split(":")
            )

            total_segundos += (
                horas * 3600 +
                minutos * 60 +
                segundos
            )

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return (
        f"{horas:02d}:"
        f"{minutos:02d}:"
        f"{segundos:02d}"
    )

def atualizar_duracao_em_aberto():

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, hora_inicio
        FROM eventos
        WHERE evento = 'EMERGENCIA_ACIONADA'
        AND hora_fim IS NULL
    """)

    registros = cursor.fetchall()

    agora = datetime.now()

    for registro in registros:

        id_evento = registro[0]
        hora_inicio = registro[1]

        inicio = datetime.strptime(
            hora_inicio,
            "%Y-%m-%d %H:%M:%S"
        )

        segundos_totais = int(
            (agora - inicio).total_seconds()
        )

        horas = segundos_totais // 3600
        minutos = (segundos_totais % 3600) // 60
        segundos = segundos_totais % 60

        duracao = (
            f"{horas:02d}:"
            f"{minutos:02d}:"
            f"{segundos:02d}"
        )

        cursor.execute("""
            UPDATE eventos
            SET duracao = ?
            WHERE id = ?
        """, (
            duracao,
            id_evento
        ))

    conexao.commit()
    conexao.close()

def parada_ativa():

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    # procura parada aberta
    cursor.execute("""
        SELECT hora_inicio
        FROM eventos
        WHERE evento = 'EMERGENCIA_ACIONADA'
        AND hora_fim IS NULL
        ORDER BY id DESC
        LIMIT 1
    """)

    registro = cursor.fetchone()

    if registro:

        inicio = datetime.strptime(
            registro[0],
            "%Y-%m-%d %H:%M:%S"
        )

        agora = datetime.now()

        segundos_totais = int(
            (agora - inicio).total_seconds()
        )

        horas = segundos_totais // 3600
        minutos = (segundos_totais % 3600) // 60
        segundos = segundos_totais % 60

        conexao.close()

        return (
            f"{horas:02d}:"
            f"{minutos:02d}:"
            f"{segundos:02d}"
        )

    # se não houver parada aberta,
    # retorna a duração da última parada encerrada

    cursor.execute("""
        SELECT duracao
        FROM eventos
        WHERE duracao IS NOT NULL
        ORDER BY id DESC
        LIMIT 1
    """)

    ultimo = cursor.fetchone()

    conexao.close()

    if ultimo:
        return ultimo[0]

    return "00:00:00"


def total_paradas(turno=None):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT COUNT(*)
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            AND turno = ?
        """, (turno,))

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
        """)

    total = cursor.fetchone()[0]

    conexao.close()

    return total

def maior_parada(turno=None):

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            AND turno = ?
            ORDER BY duracao DESC
            LIMIT 1
        """, (turno,))

    else:

        cursor.execute("""
            SELECT duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            ORDER BY duracao DESC
            LIMIT 1
        """)

    resultado = cursor.fetchone()

    conexao.close()

    if resultado:
        return resultado[0]

    return "00:00:00"

def paradas_por_estacao(turno=None):

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT estacao,
                   COUNT(*)
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            AND turno = ?
            GROUP BY estacao
            ORDER BY estacao
        """, (turno,))

    else:

        cursor.execute("""
            SELECT estacao,
                   COUNT(*)
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            GROUP BY estacao
            ORDER BY estacao
        """)

    dados = cursor.fetchall()

    conexao.close()

    return dados

def estacao_mais_critica(turno=None):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT estacao,
                   COUNT(*) as total
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            AND turno = ?
            GROUP BY estacao
        """, (turno,))

    else:

        cursor.execute("""
            SELECT estacao,
                   COUNT(*) as total
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            GROUP BY estacao
        """)

    dados = cursor.fetchall()

    conexao.close()

    if not dados:
        return "-"

    maior = max(total for _, total in dados)

    estacoes = []

    for estacao, total in dados:

        if total == maior:
            estacoes.append(f"E{estacao}")

    return f"{' | '.join(estacoes)} ({maior})"

def tempo_por_estacao(turno=None):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT estacao, duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            AND turno = ?
        """, (turno,))

    else:

        cursor.execute("""
            SELECT estacao, duracao
            FROM eventos
            WHERE duracao IS NOT NULL
        """)

    dados = cursor.fetchall()

    conexao.close()

    totais = {}

    for estacao, duracao in dados:

        if estacao not in totais:
            totais[estacao] = 0

        h, m, s = map(int, duracao.split(":"))

        totais[estacao] += (
            h * 3600 +
            m * 60 +
            s
        )

    resultado = []

    for estacao, segundos in totais.items():

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_rest = segundos % 60

        resultado.append(
            (
                estacao,
                f"{horas:02d}:{minutos:02d}:{segundos_rest:02d}"
            )
        )

    return sorted(resultado)

def estacao_mais_impactante(turno=None):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    if turno and turno != "Todos":

        cursor.execute("""
            SELECT estacao, duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            AND turno = ?
        """, (turno,))

    else:

        cursor.execute("""
            SELECT estacao, duracao
            FROM eventos
            WHERE duracao IS NOT NULL
        """)

    registros = cursor.fetchall()

    conexao.close()

    totais = {}

    for estacao, duracao in registros:

        h, m, s = map(int, duracao.split(":"))

        segundos = h * 3600 + m * 60 + s

        totais[estacao] = totais.get(estacao, 0) + segundos

    if not totais:
        return "-"

    maior_tempo = max(totais.values())

    estacoes = []

    for estacao, tempo in totais.items():

        if tempo == maior_tempo:
            estacoes.append(f"E{estacao}")

    minutos = maior_tempo // 60

    return f"{' | '.join(estacoes)} ({minutos} min)"

def percentual_paradas_por_estacao(turno=None):

    dados = paradas_por_estacao(turno)

    total = sum(qtd for _, qtd in dados)

    resultado = []

    for estacao, quantidade in dados:

        percentual = (
            quantidade / total * 100
            if total > 0 else 0
        )

        resultado.append(
            (
                estacao,
                f"{percentual:.0f}%"
            )
        )

    return resultado

def disponibilidade_linha(turno=None):

    tempo_paradas = tempo_total_paradas(turno)

    h, m, s = map(int, tempo_paradas.split(":"))

    segundos_paradas = (
        h * 3600 +
        m * 60 +
        s
    )

    if turno == "1º TURNO":
        segundos_planejados = 539 * 60

    elif turno == "2º TURNO":
        segundos_planejados = 499 * 60

    else:
        segundos_planejados = 1038 * 60

    disponibilidade = (
        (segundos_planejados - segundos_paradas)
        / segundos_planejados
    ) * 100

    if disponibilidade < 0:
        disponibilidade = 0

    return f"{disponibilidade:.1f}%"

def tempo_total_periodo(periodo):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT duracao
        FROM eventos
        WHERE duracao IS NOT NULL
        AND periodo = ?
    """, (periodo,))

    registros = cursor.fetchall()

    conexao.close()

    total_segundos = 0

    for registro in registros:

        duracao = registro[0]

        if duracao:

            h, m, s = map(
                int,
                duracao.split(":")
            )

            total_segundos += (
                h * 3600 +
                m * 60 +
                s
            )

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return (
        f"{horas:02d}:"
        f"{minutos:02d}:"
        f"{segundos:02d}"
    )

def percentual_tempo_perdido(turno=None):

    tempos = tempo_por_estacao(turno)

    total_segundos = 0

    for _, tempo in tempos:

        h, m, s = map(int, tempo.split(":"))

        total_segundos += (
            h * 3600 +
            m * 60 +
            s
        )

    resultado = []

    for estacao, tempo in tempos:

        h, m, s = map(int, tempo.split(":"))

        segundos = (
            h * 3600 +
            m * 60 +
            s
        )

        percentual = (
            segundos / total_segundos * 100
            if total_segundos > 0 else 0
        )

        resultado.append(
            (
                estacao,
                f"{percentual:.0f}%"
            )
        )

    return resultado


def paradas_por_estacao_turno_periodo(
    turno,
    periodo
):

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    if turno != "Todos":

        cursor.execute("""
            SELECT estacao,
                   COUNT(*)
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            AND turno = ?
            AND periodo = ?
            GROUP BY estacao
            ORDER BY estacao
        """, (
            turno,
            periodo
        ))

    else:

        cursor.execute("""
            SELECT estacao,
                   COUNT(*)
            FROM eventos
            WHERE evento='EMERGENCIA_ACIONADA'
            AND periodo = ?
            GROUP BY estacao
            ORDER BY estacao
        """, (
            periodo,
        ))

    dados = cursor.fetchall()

    conexao.close()

    return dados

def tempo_por_estacao_turno_periodo(
    turno,
    periodo
):

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    if turno != "Todos":

        cursor.execute("""
            SELECT estacao,
                   duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            AND turno = ?
            AND periodo = ?
        """, (
            turno,
            periodo
        ))

    else:

        cursor.execute("""
            SELECT estacao,
                   duracao
            FROM eventos
            WHERE duracao IS NOT NULL
            AND periodo = ?
        """, (
            periodo,
        ))

    dados = cursor.fetchall()

    conexao.close()

    totais = {}

    for estacao, duracao in dados:

        h, m, s = map(
            int,
            duracao.split(":")
        )

        segundos = (
            h * 3600 +
            m * 60 +
            s
        )

        totais[estacao] = (
            totais.get(estacao, 0)
            + segundos
        )

    resultado = []

    for estacao, segundos in totais.items():

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_rest = segundos % 60

        resultado.append(

            (
                estacao,

                f"{horas:02d}:"
                f"{minutos:02d}:"
                f"{segundos_rest:02d}"

            )

        )

    return sorted(resultado)

def percentual_paradas_turno_periodo(
    turno,
    periodo
):

    dados = paradas_por_estacao_turno_periodo(
        turno,
        periodo
    )

    total = sum(
        quantidade
        for _, quantidade in dados
    )

    if total == 0:
        return []

    resultado = []

    for estacao, quantidade in dados:

        percentual = round(
            (quantidade / total) * 100
        )

        resultado.append(
            (
                estacao,
                f"{percentual}%"
            )
        )

    return resultado

def percentual_tempo_perdido_turno_periodo(
    turno,
    periodo
):

    dados = tempo_por_estacao_turno_periodo(
        turno,
        periodo
    )

    total_segundos = 0

    tempos_convertidos = []

    for estacao, tempo in dados:

        h, m, s = map(
            int,
            tempo.split(":")
        )

        segundos = (
            h * 3600 +
            m * 60 +
            s
        )

        tempos_convertidos.append(
            (
                estacao,
                segundos
            )
        )

        total_segundos += segundos

    if total_segundos == 0:
        return []

    resultado = []

    for estacao, segundos in tempos_convertidos:

        percentual = round(
            (segundos / total_segundos)
            * 100
        )

        resultado.append(

            (
                estacao,
                f"{percentual}%"
            )

        )

    return resultado

def salvar_historico_turno(

    data,
    turno,
    total_paradas,
    tempo_total,
    maior_parada,
    estacao_recorrente,
    estacao_impactante,
    disponibilidade

):

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    cursor.execute("""

        INSERT INTO historico_turnos (

            data,
            turno,
            total_paradas,
            tempo_total,
            maior_parada,
            estacao_recorrente,
            estacao_impactante,
            disponibilidade

        )

        VALUES (

            ?, ?, ?, ?, ?, ?, ?, ?

        )

    """, (

        data,
        turno,
        total_paradas,
        tempo_total,
        maior_parada,
        estacao_recorrente,
        estacao_impactante,
        disponibilidade

    ))

    conexao.commit()

    conexao.close()

def listar_historico_turnos():

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    cursor.execute("""

        SELECT *

        FROM historico_turnos

        ORDER BY id DESC

    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados


def listar_historico_turnos():

    conexao = sqlite3.connect(BANCO)

    cursor = conexao.cursor()

    cursor.execute("""

        SELECT
            data,
            turno,
            total_paradas,
            maior_parada,
            tempo_total,
            estacao_recorrente,
            estacao_impactante,
            disponibilidade
        FROM historico_turnos
        ORDER BY id DESC

    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados

def gerar_historico_turno(turno):

    salvar_historico_turno(
        data=datetime.now().strftime("%d/%m/%Y"),
        turno=turno,
        total_paradas=total_paradas(turno),
        tempo_total=tempo_total_paradas(turno),
        maior_parada=maior_parada(turno),
        estacao_recorrente=estacao_mais_critica(turno),
        estacao_impactante=estacao_mais_impactante(turno),
        disponibilidade=disponibilidade_linha(turno)
    )


def historico_existe(data, turno):

    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM historico_turnos
        WHERE data = ?
        AND turno = ?
    """, (data, turno))

    total = cursor.fetchone()[0]

    conexao.close()

    return total > 0

def atualizar_historico_turno(
    data,
    turno,
    total_paradas,
    tempo_total,
    maior_parada,
    estacao_recorrente,
    estacao_impactante,
    disponibilidade
):
    conexao = sqlite3.connect(BANCO)
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE historico_turnos
        SET
            total_paradas=?,
            tempo_total=?,
            maior_parada=?,
            estacao_recorrente=?,
            estacao_impactante=?,
            disponibilidade=?
        WHERE
            data=? AND turno=?
    """,
    (
        total_paradas,
        tempo_total,
        maior_parada,
        estacao_recorrente,
        estacao_impactante,
        disponibilidade,
        data,
        turno
    ))

    conexao.commit()
    conexao.close()
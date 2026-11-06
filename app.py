from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for
)

from modbus import (
    ler_emergencias,
    acionar_emergencia,
    liberar_emergencia
)

from banco import (
    criar_banco,
    registrar_evento,
    listar_eventos,
    contar_paradas,
    finalizar_parada,
    emergencia_aberta,
    tempo_total_paradas,
    atualizar_duracao_em_aberto,
    parada_ativa,
    total_paradas,
    maior_parada,
    paradas_por_estacao,
    estacao_mais_critica,
    estacao_mais_impactante,
    tempo_por_estacao,
    disponibilidade_linha,
    percentual_paradas_por_estacao,
    percentual_tempo_perdido,
    tempo_total_periodo,
    paradas_por_estacao_turno_periodo,
    tempo_por_estacao_turno_periodo,
    percentual_paradas_turno_periodo,
    percentual_tempo_perdido_turno_periodo,
    salvar_historico_turno,
    listar_historico_turnos,
    historico_existe,
    atualizar_historico_turno


)

from producao import identificar_turno_periodo

app = Flask(__name__)

criar_banco()


@app.route("/")
def index():

    turno, periodo = identificar_turno_periodo()

    if turno == "FORA DE PRODUÇÃO":
        status_linha = "FORA DE PRODUÇÃO"
    else:
        status_linha = "PRODUZINDO"

    return render_template(
        "index.html",
        turno=turno,
        periodo=periodo,
        status_linha=status_linha
    )

@app.route("/api/emergencias")
def emergencias():

    try:

        estados = ler_emergencias()

        if estados is None:
            return jsonify({
                "erro":"Sem comunicação com o CLP"
            })

        return jsonify({
            "E1": int(estados[0]),
            "E2": int(estados[1]),
            "E3": int(estados[2]),
            "E4": int(estados[3]),
            "E5": int(estados[4]),
            "E6": int(estados[5])
        })

    except Exception as erro:

        return jsonify({
            "erro": str(erro)
        })
    
@app.route("/api/estacoes")
def api_estacoes():

    return jsonify({

        "E1": emergencia_aberta(1),
        "E2": emergencia_aberta(2),
        "E3": emergencia_aberta(3),
        "E4": emergencia_aberta(4),
        "E5": emergencia_aberta(5),
        "E6": emergencia_aberta(6)

    })

@app.route("/api/acionar/<int:numero>")
def acionar(numero):

    acionar_emergencia(numero)

    return jsonify({
        "mensagem": f"E{numero} acionada"
    })


@app.route("/api/liberar/<int:numero>")
def liberar(numero):

    liberar_emergencia(numero)

    return jsonify({
        "mensagem": f"E{numero} liberada"
    })

@app.route("/api/evento/<int:estacao>/<evento>")
def registrar_evento_api(estacao, evento):

    turno, periodo = identificar_turno_periodo()

    if evento == "EMERGENCIA_ACIONADA":

        if not emergencia_aberta(estacao):

            registrar_evento(
                estacao,
                evento,
                turno,
                periodo
            )

    elif evento == "EMERGENCIA_LIBERADA":

        if emergencia_aberta(estacao):

            finalizar_parada(estacao)

            registrar_evento(
                estacao,
                evento,
                turno,
                periodo
            )

    return {
        "status": "OK"
    }

@app.route("/api/eventos")
def api_eventos():

    atualizar_duracao_em_aberto()

    dados = listar_eventos()

    return jsonify(dados)
    
@app.route("/eventos")
def tela_eventos():

    eventos = listar_eventos()

    return render_template(
        "eventos.html",
        eventos=eventos
    )

@app.route("/dados")
def dados():

    turno, periodo = identificar_turno_periodo()

    if turno == "FORA DE PRODUÇÃO":
        status_linha = "FORA DE PRODUÇÃO"
    else:
        status_linha = "PRODUZINDO"

    return {
    "status": status_linha,
    "turno": turno,
    "periodo": periodo,
    "paradas": contar_paradas(turno),
    "tempo": tempo_total_paradas(),
    "tempo_periodo": tempo_total_periodo(periodo),
    "parada_atual": parada_ativa()
}


@app.route("/api/paradas")
def paradas():

    turno, periodo = identificar_turno_periodo()

    total = contar_paradas(turno)

    return {
        "paradas": total,
        "turno": turno,
        "periodo": periodo
    }

@app.route("/api/status")
def status_clp():

    estados = ler_emergencias()

    if estados is None:

        return {
            "clp": "OFFLINE"
        }

    return {
        "clp": "ONLINE"
    }


@app.route("/relatorios")
def relatorios():

    turno = request.args.get(
    "turno",
    "Todos")
    
    percentuais = percentual_paradas_por_estacao(turno)

    tempo_perdido = percentual_tempo_perdido(turno)

    if percentuais:  
        maior_percentual = max(
            int(p[1].replace("%", ""))
            for p in percentuais
        )

    else:
        maior_percentual = "Sem Dados"

    if tempo_perdido:
        maior_tempo_perdido = max(
            int(p[1].replace("%", ""))
            for p in tempo_perdido
        )

    else:
        maior_tempo_perdido = "Sem Dados"

        
    estacoes_p1 = paradas_por_estacao_turno_periodo(
        turno,
        "1º PERÍODO"
    )

    estacoes_p2 = paradas_por_estacao_turno_periodo(
        turno,
        "2º PERÍODO"
    )

    tempos_p1 = tempo_por_estacao_turno_periodo(
        turno,
        "1º PERÍODO"
    )

    tempos_p2 = tempo_por_estacao_turno_periodo(
        turno,
        "2º PERÍODO"
    )

    percentuais_p1 =percentual_paradas_turno_periodo(
        turno,
        "1º PERÍODO"
    )

    percentuais_p2 =percentual_paradas_turno_periodo(
        turno,
        "2º PERÍODO"
    )

    tempo_perdido_p1 =percentual_tempo_perdido_turno_periodo(
        turno,
        "1º PERÍODO"
    )

    tempo_perdido_p2 =percentual_tempo_perdido_turno_periodo(
        turno,
        "2º PERÍODO"
    )


    return render_template(
        "relatorios.html",
        turno_selecionado=turno,
           
        total_paradas=total_paradas(turno),

        tempo_total=tempo_total_paradas(turno),

        maior_parada=maior_parada(turno),

        estacao_critica=estacao_mais_critica(turno),

        estacao_impactante=estacao_mais_impactante(turno),

        estacoes=paradas_por_estacao(turno),

        tempos_estacao=tempo_por_estacao(turno),

        disponibilidade=disponibilidade_linha(turno),

        percentuais=percentuais,
        
        tempo_perdido=tempo_perdido,
        
        maior_percentual=maior_percentual,

        maior_tempo_perdido=maior_tempo_perdido,

        estacoes_p1=estacoes_p1,

        estacoes_p2=estacoes_p2,

        tempos_p1=tempos_p1,

        tempos_p2=tempos_p2,

        percentuais_p1=percentuais_p1,

        percentuais_p2=percentuais_p2,

        tempo_perdido_p1=tempo_perdido_p1,

        tempo_perdido_p2=tempo_perdido_p2,

    )

@app.route("/api/relatorios")
def api_relatorios():

    turno = request.args.get(
        "turno",
        "Todos"
    )

    return jsonify({

        "tempo_total":
        tempo_total_paradas(turno),

        "maior_parada":
        maior_parada(turno),

        "disponibilidade":
        disponibilidade_linha(turno)

    })

@app.route("/teste-turnos")
def teste_turnos():

    import sqlite3

    conexao = sqlite3.connect("database/supervisorio.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT turno, COUNT(*)
        FROM eventos
        GROUP BY turno
    """)

    dados = cursor.fetchall()

    conexao.close()

    return {
        "turnos": dados
    }

@app.route("/teste-horario")
def teste_horario():

    from producao import identificar_turno_periodo

    turno, periodo = identificar_turno_periodo()

    return {
        "turno": turno,
        "periodo": periodo
    }

@app.route("/configuracoes")
def configuracoes():

    return render_template(
        "configuracoes.html"
    )

@app.route("/teste-paradas-abertas")
def teste_paradas_abertas():

    import sqlite3

    conexao = sqlite3.connect("database/supervisorio.db")

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id,
               estacao,
               evento,
               hora_inicio,
               hora_fim
        FROM eventos
        WHERE evento='EMERGENCIA_ACIONADA'
        AND hora_fim IS NULL
    """)

    dados = cursor.fetchall()

    conexao.close()

    return {"abertas": dados}


@app.route("/teste-historico")
def teste_historico():

    salvar_historico_turno(

        "26/07/2026",
        "1º TURNO",
        8,
        "01:29:40",
        "00:18:30",
        "E1",
        "E2 (42 min)",
        "96,2%"

    )

    return {"status": "OK"}

@app.route("/ver-historico")
def ver_historico():

    return {

        "dados":
        listar_historico_turnos()

    }

@app.route("/historico")
def historico():

    return render_template(

        "historico.html",

        historicos=
        listar_historico_turnos()

    )

from datetime import datetime
from producao import identificar_turno_periodo

@app.route("/salvar-relatorio")
@app.route("/salvar-relatorio")
def salvar_relatorio():

    turno_atual, periodo = identificar_turno_periodo()
    data = datetime.now().strftime("%d/%m/%Y")

    if historico_existe(data, turno_atual):

        atualizar_historico_turno(
            data,
            turno_atual,
            total_paradas(turno_atual),
            tempo_total_paradas(turno_atual),
            maior_parada(turno_atual),
            estacao_mais_critica(turno_atual),
            estacao_mais_impactante(turno_atual),
            disponibilidade_linha(turno_atual)
        )

    else:

        salvar_historico_turno(
            data,
            turno_atual,
            total_paradas(turno_atual),
            tempo_total_paradas(turno_atual),
            maior_parada(turno_atual),
            estacao_mais_critica(turno_atual),
            estacao_mais_impactante(turno_atual),
            disponibilidade_linha(turno_atual)
        )

    return redirect(url_for("historico"))


@app.route("/limpar-duplicados")
def limpar_duplicados():

    import sqlite3

    conexao = sqlite3.connect("database/supervisorio.db")
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM historico_turnos
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM historico_turnos
            GROUP BY data, turno
        )
    """)

    conexao.commit()
    conexao.close()

    return {"status": "OK"}


if __name__ == "__main__":

    print(app.url_map)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

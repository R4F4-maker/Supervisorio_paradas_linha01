console.log("SUPERVISAO.JS CARREGOU");


let estadoAnteriores = [0,0,0,0,0,0];



// ===============================
// LEITURA DAS EMERGÊNCIAS
// ===============================

function atualizarEmergencias() {

    fetch("/api/estacoes")

    .then(resposta => resposta.json())

    .then(dados => {


        let emergenciaAtiva = false;


        for (let i = 1; i <= 6; i++) {


            let estado = dados["E" + i];


            let indicador = document.getElementById("indicador" + i);

            let status = document.getElementById("status" + i);



            // Atualiza indicador visual

            if (estado) {


                indicador.classList.add("ativo");

                status.innerHTML = "ACIONADA";

                emergenciaAtiva = true;


            } else {


                indicador.classList.remove("ativo");

                status.innerHTML = "NORMAL";


            }



            // ===============================
            // NOVO ACIONAMENTO
            // ===============================

            if (estado === 1 && estadoAnteriores[i-1] === 0) {


                console.log(
                    "Emergência acionada: Estação " + i
                );


    
                fetch(
                    "/api/evento/" 
                    + i 
                    + "/EMERGENCIA_ACIONADA"
                );


            }



            // ===============================
            // LIBERAÇÃO DA EMERGÊNCIA
            // ===============================


            if (estado === 0 && estadoAnteriores[i-1] === 1) {


                console.log(
                    "Emergência liberada: Estação " + i
                );



                fetch(
                    "/api/evento/" 
                    + i 
                    + "/EMERGENCIA_LIBERADA"
                );


            }



            // Guarda estado anterior

            estadoAnteriores[i-1] = estado;


        }



        // Atualiza status geral da linha


        let statusLinha =
        document.getElementById("statusLinha");



        if (emergenciaAtiva) {


            statusLinha.innerHTML = "PARADA";

            statusLinha.style.color = "#F43606";


        } else {


            statusLinha.innerHTML = "PRODUZINDO";

            statusLinha.style.color = "#00FF66";


        }



    })

    .catch(erro => {

        console.log(
            "Erro na comunicação:",
            erro
        );

    });

}



// ===============================
// RELÓGIO
// ===============================

function atualizarHora(){


    let data = new Date();


    document.getElementById("hora").innerHTML =
    data.toLocaleString();


}

function atualizarContadorParadas(){

    fetch("/api/paradas")

    .then(response => response.json())

    .then(dados => {

        document.getElementById(
            "contadorParadas"
        ).innerHTML = dados.paradas;

    });

}

setInterval(
    atualizarContadorParadas,
    1000
);

atualizarContadorParadas();

setInterval(
    atualizarHora,
    1000
);


atualizarHora();



// ===============================
// ATUALIZAÇÃO DAS EMERGÊNCIAS
// ===============================


setInterval(
    atualizarEmergencias,
    3000
);


atualizarEmergencias();



// ===============================
// TURNO / PERÍODO / TEMPO
// ===============================


function atualizarSupervisao(){


    fetch("/dados")

    .then(response => response.json())


    .then(dados => {


        document.getElementById("turno").innerHTML =
        dados.turno;


        document.getElementById("periodo").innerHTML =
        dados.periodo;

        document.getElementById("paradaAtual").innerHTML = 
        dados.parada_atual;

        document.getElementById("tempoParadas").innerHTML =
        dados.tempo;
        
        document.getElementById("tempoPeriodo").innerHTML =
        dados.tempo_periodo;



    });


}



setInterval(
    atualizarSupervisao,
    1000
);

function atualizarStatusSistema(){

    fetch("/api/status")

    .then(response => response.json())

    .then(dados => {

        let statusSistema =
        document.getElementById(
            "statusSistema"
        );

        if(dados.clp === "ONLINE"){

            statusSistema.innerHTML =
            "🟢 CLP ONLINE | " +
            "🟢 Banco OK | " +
            "🟢 Comunicação OK | " +
            "Versão 1.0";

        }else{

            statusSistema.innerHTML =
            "🔴 CLP OFFLINE | " +
            "🟢 Banco OK | " +
            "🔴 Sem Comunicação | " +
            "Versão 1.0";

        }

    });

}

setInterval(
    atualizarStatusSistema,
    3000
);

atualizarStatusSistema();

atualizarSupervisao();

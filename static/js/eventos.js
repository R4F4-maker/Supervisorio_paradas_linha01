console.log("EVENTOS.JS CARREGADO");

function carregarEventos() {

    fetch("/api/eventos")
        .then(res => res.json())
        .then(dados => {

            let tabela = document.getElementById("listaEventos");
            tabela.innerHTML = "";

            dados.forEach(evento => {

                let linha = document.createElement("tr");

                let classe = "";

                if (evento[2] === "EMERGENCIA_ACIONADA") {
                    classe = "evento-acionada";
                }

                if (evento[2] === "EMERGENCIA_LIBERADA") {
                    classe = "evento-liberada";
                }

                linha.innerHTML = `
                    <td>${evento[0]}</td>
                    <td>E${evento[1]}</td>
                    <td class="${classe}">${evento[2]}</td>
                    <td>${evento[3]}</td>
                    <td>${evento[4]}</td>
                    <td>${evento[5] || "-"}</td>
                `;

                tabela.appendChild(linha);

            });

        })
        .catch(erro => {

            console.log("Erro ao carregar eventos:", erro);

        });

}

carregarEventos();

setInterval(carregarEventos, 1000);

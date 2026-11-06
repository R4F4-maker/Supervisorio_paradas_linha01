from pymodbus.client import ModbusTcpClient

IP_CLP = "192.168.0.60"
PORTA = 502

SIMULACAO = True

EMERGENCIAS = [False, False, False, False, False, False]

#print("MODBUS.PY CARREGADO - SIMULACAO =", SIMULACAO)

def ler_emergencias():

    # print("Entrou na função ler_emergencias()")

    if SIMULACAO:
        return EMERGENCIAS
    
    client = ModbusTcpClient(IP_CLP, port=PORTA)

    if not client.connect():
        return None

    leitura = client.read_coils(address=0, count=6)

    client.close()

    if leitura.isError():
        return None

    return leitura.bits[:6]


def acionar_emergencia(numero):
    if 1 <= numero <=6:
        EMERGENCIAS[numero-1] = True


def liberar_emergencia(numero):
    if 1 <= numero <=6:
        EMERGENCIAS[numero-1] = False

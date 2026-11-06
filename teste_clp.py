from pymodbus.client import ModbusTcpClient

IP_CLP = "192.168.0.60"

client = ModbusTcpClient(IP_CLP, port=502)

if client.connect():
    print("CLP conectado!")

    leitura = client.read_coils(address=0, count=6)

    if leitura.isError():
        print(f"Erro na leitura Modbus: {leitura}")
    else:
        print("Entradas:")
        print(leitura.bits)

    client.close()

else:
    print("Falha ao conectar no CLP")
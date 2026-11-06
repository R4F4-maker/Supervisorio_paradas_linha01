from modbus import ler_emergencias,acionar_emergencia,liberar_emergencia
import time

print("Monitor iniciado...\n")

while True:
    estados = ler_emergencias()

    if estados is None:
        print("\rSem comunicacao com o CLP", end="", flush=True)

    else:
        print(
            f"\rE1:{int(estados[0])} "
            f"E2:{int(estados[1])} "
            f"E3:{int(estados[2])} "
            f"E4:{int(estados[3])} "
            f"E5:{int(estados[4])} "
            f"E6:{int(estados[5])}",
            end="",
            flush=True
        )

    time.sleep(0.2)
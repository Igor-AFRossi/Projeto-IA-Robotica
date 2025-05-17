from controller import Supervisor
import math

TIME_STEP = 32
QtddSensoresProx = 8
QtddLeds = 10

# Função para ordenar as caixas da mais próxima para a mais distante do robô
def ordenar_caixas_por_proximidade(pos_caixas, pos_robo):
    menor_dist = float('inf')
    indice_mais_proxima = 0
    for i, pos in enumerate(pos_caixas):
        dx = pos[0] - pos_robo[0]
        dz = pos[1] - pos_robo[1]
        dist = math.sqrt(dx ** 2 + dz ** 2)
        if dist < menor_dist:
            menor_dist = dist
            indice_mais_proxima = i
    # Move a caixa mais próxima para a primeira posição da lista
    if indice_mais_proxima != 0:
        pos_caixas[0], pos_caixas[indice_mais_proxima] = pos_caixas[indice_mais_proxima], pos_caixas[0]

# Inicializa o supervisor do Webots
robot = Supervisor()

# Inicialização dos motores e configuração para controle manual de velocidade
motor_esq = robot.getDevice("left wheel motor")
motor_dir = robot.getDevice("right wheel motor")
motor_esq.setPosition(float('inf'))
motor_dir.setPosition(float('inf'))
motor_esq.setVelocity(0)
motor_dir.setVelocity(0)

# Inicializa sensores de proximidade
sensor_prox = []
for i in range(QtddSensoresProx):
    sensor = robot.getDevice(f"ps{i}")
    sensor.enable(TIME_STEP)
    sensor_prox.append(sensor)

# Inicializa o LED principal
led0 = robot.getDevice("led0")
led0.set(-1)  # Desliga o LED inicialmente

# Coleta posições das caixas e armazena referência a cada uma
numero_de_caixas = 20
pos_caixas = []
caixas_dict = {}

for i in range(1, numero_de_caixas + 1):
    nome = f"CAIXA{i}"
    caixa = robot.getFromDef(nome)
    if caixa is not None:
        caixas_dict[nome] = caixa
        pos = caixa.getPosition()
        pos_caixas.append(pos)
    else:
        print(f"Erro: {nome} não encontrada")

# Variáveis de controle do comportamento
caixa_moveu = False
passos_empurrando = 0
tempo_empurrar_max = 30  # Número de ciclos para tentar empurrar

# Variáveis para controle do piscar do LED
contador_led = 0
estado_led = False

# Loop principal do robô
while robot.step(TIME_STEP) != -1:
    
    # Enquanto houver caixas e nenhuma foi identificada como leve
    if len(pos_caixas) > 0 and not caixa_moveu:
        # Posição e orientação do robô
        pos_robo = robot.getSelf().getPosition()
        rot_robo = robot.getSelf().getOrientation()

        # Ordena as caixas pela distância ao robô
        ordenar_caixas_por_proximidade(pos_caixas, pos_robo)

        # Lê os sensores de proximidade
        leitura_sensor_prox = []
        for sensor in sensor_prox:
            valor = sensor.getValue() - 60
            leitura_sensor_prox.append(valor)

        pos_primeira = pos_caixas[0]

        # Função auxiliar para comparar posições com tolerância
        def pos_iguais(pos1, pos2, tolerancia=1e-4):
            return all(abs(a - b) < tolerancia for a, b in zip(pos1, pos2))

        # Encontra o nome da caixa que está na posição atual
        for nome_caixa, caixa in caixas_dict.items():
            if pos_iguais(pos_primeira, caixa.getPosition()):
                alvo = nome_caixa
                break

        # Pega a posição atual da caixa alvo
        pos_atual = caixas_dict[alvo].getPosition()

        # Calcula direção e erro angular entre o robô e a caixa
        dx = pos_caixas[0][0] - pos_robo[0]
        dy = pos_caixas[0][1] - pos_robo[1]
        angulo_desejado = math.atan2(dy, dx)
        angulo_robo = math.atan2(rot_robo[1], rot_robo[0])
        erro_angular = angulo_desejado + angulo_robo
        distancia = math.sqrt(dx ** 2 + dy ** 2)

        print('Alvo:', alvo)

        # Movimento do robô: segue em frente se estiver alinhado, senão gira para alinhar
        if -0.15 < erro_angular <= 0.15:
            velocidade = 4.0
            acelerador_esq = 1.0
            acelerador_dir = 1.0
        else:
            velocidade = 2.0
            acelerador_esq = 1.0
            acelerador_dir = -1.0
            print('Desviando de obstaculo')

        # Verifica se está empurrando a caixa e se ela se moveu
        if distancia < 0.09:
            passos_empurrando += 1
            if passos_empurrando >= tempo_empurrar_max:
                if not pos_iguais(pos_atual, pos_caixas[0]):
                    caixa_moveu = True  # Caixa leve identificada
                else:
                    pos_caixas.pop(0)  # Caixa pesada, ignora e passa para a próxima
                    passos_empurrando = 0
        else:
            passos_empurrando = 0

    # Se não houver mais caixas e nenhuma foi leve
    elif len(pos_caixas) == 0 and not caixa_moveu:
        print("Caixa leve não encontrada")
        acelerador_esq = 0.0
        acelerador_dir = 0.0
        velocidade = 0.0

    # Se uma caixa leve foi identificada
    elif caixa_moveu:
        print(f"Caixa leve encontrada: {alvo}")
        # Gira no próprio eixo
        acelerador_esq = 1.0
        acelerador_dir = -1.0
        velocidade = 2.0

        # Pisca o LED alternando estado a cada 10 ciclos
        contador_led += 1
        if contador_led >= 10:
            estado_led = not estado_led
            led0.set(1 if estado_led else 0)
            contador_led = 0

    # Aplica as velocidades calculadas aos motores
    motor_esq.setVelocity(velocidade * acelerador_esq)
    motor_dir.setVelocity(velocidade * acelerador_dir)

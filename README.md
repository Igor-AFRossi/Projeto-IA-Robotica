# Projeto-IA-Robotica

- Enzo Bozzani Martins - 24.122.020-1
- Igor Augusto Fiorini Rossi - 24.122.023-5

Este código implementa o controle de um robô supervisor no Webots que tem como objetivo identificar qual entre várias caixas espalhadas pelo ambiente é a caixa leve, ou seja, aquela que pode ser movida com um empurrão. O robô se orienta pela posição das caixas e seleciona sempre a mais próxima para tentar empurrar. Se após um tempo a caixa se mover, ela é considerada leve; caso contrário, é descartada e a próxima é testada. Quando a caixa leve é encontrada, o robô gira no próprio eixo como sinal de identificação e começa a piscar o LED como forma de alerta visual.

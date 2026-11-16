# SPEED RACER - 8 FASES

Instale: `pip install -r requirements.txt`
Execute: `python main.py`

Fases: Cidade Inicial, Estrada Costeira, Distrito Industrial, Circuito Noturno, Deserto Turbo, Serra Extrema, Metrópole Neon e Campeonato Final.

Cada fase tem cenário próprio, corrida classificatória e chefe. Termine no Top 3 da classificatória para liberar o chefe. Termine no Top 3 contra o chefe para liberar a fase seguinte e mostrar a tela especial de desbloqueio.

Teclas: W/S acelerar/frear, A/D direção, ESPAÇO turbo, E escudo, R reparo.

Para preservar progresso, copie `speed_racer_save.json` da pasta antiga para esta pasta.


## Sistema de posições
12 competidores fixos (você + 11 adversários). A classificação é recalculada por progresso real, com aviso ao ultrapassar ou perder posição. Os 3 primeiros recebem premiação.


## Corridas contra chefes
- Classificatórias: 12 pilotos, Top 3 avança.
- Chefe: apenas você e o chefe (1 x 1), só o 1º lugar vence e libera a próxima fase.
- Chefe tem velocidade máxima fixa 8.3, acima do carro inicial sem upgrades (8.0), abaixo do carro inicial com 1 melhoria de motor (8.55).
- Derrota no duelo não rende prêmio nem desbloqueio.


## Atualização: 4 corredores e saldo infinito
- Classificatórias: jogador + 3 rivais (4 posições no ranking).
- Duelo de chefe: apenas jogador e chefe (2 posições).
- Dinheiro ilimitado: saldo é restaurado automaticamente para 999.999.999.999 ao carregar e salvar, inclusive com saves antigos. Interface mostra ∞.
- Premiações Top 3, upgrades, loja e oito fases mantidos.


## Atualização: quatro pistas
- Estrada com quatro faixas visíveis.
- Classificatória: jogador na faixa 2; rivais nas faixas 1, 3 e 4, todos na mesma linha de largada.
- Chefe: largada em uma das outras três faixas, nunca na do jogador.
- Itens e obstáculos distribuídos entre as quatro faixas.


LOJA NOVA: TAB ou clique para alternar CARROS e HABILIDADES. Na aba carros, A/D ou setas esquerda/direita trocam de página; setas cima/baixo selecionam e ENTER compra/equipa. Clique duas vezes no mesmo carro para comprar/equipar.


## Botão Voltar na loja
Clique em **< VOLTAR** no canto superior esquerdo para retornar ao menu sem usar ESC.

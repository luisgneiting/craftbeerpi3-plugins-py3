# PIDBoil

Controlador de temperatura para kettle com algoritmo PID e modo especial de fervura (boil). Quando a temperatura alvo está acima do limiar de fervura configurado, o controlador vai a 100% de potência em vez de usar o cálculo PID normal.

---

## Como funciona

**Abaixo do limiar de fervura:** o algoritmo PID calcula a potência necessária para chegar na temperatura alvo com precisão e sem sobrepassar.

**Acima do limiar de fervura:** potência vai direto a 100% — não faz sentido modular durante a fervura, só manter fervendo.

```
Temperatura:  25°C ──────────────── 99°C ──── [fervura] ──── 100°C
Potência:     [  PID calcula  ]           [100% fixo]
```

---

## Pré-requisitos

Nenhuma dependência extra. O plugin está incluído no repositório e funciona com Python 3.13.

---

## Como configurar na interface web

1. Acesse o CraftBeerPi: `http://<ip-do-rpi>:5000`
2. Vá em **System → Kettles**
3. Edite o kettle desejado (ou crie um novo)
4. No campo **Logic**, selecione `PIDBoil`
5. Preencha os parâmetros e clique em **Save**

---

## Parâmetros

| Parâmetro | Descrição | Valor padrão recomendado |
|-----------|-----------|--------------------------|
| `P` | Ganho proporcional — reage ao erro atual | `117.0` |
| `I` | Ganho integral — corrige erro acumulado ao longo do tempo | `0.33` |
| `D` | Ganho derivativo — amorte oscilações | `41.58` |
| `Max output %` | Potência máxima permitida (0–100) | `100` |
| `Boil threshold` | Temperatura a partir da qual vai a 100% | `99` |

> **Dica:** Use o plugin [PIDAutoTune](../PIDAutoTune/README.md) para calcular automaticamente os valores de P, I e D ideais para o seu sistema.

---

## Ajuste manual dos parâmetros PID

Se não quiser usar o AutoTune, comece com os valores padrão e ajuste assim:

**P muito alto →** temperatura oscila em torno do alvo (sobe e desce sem parar)
→ Diminua P pela metade

**P muito baixo →** demora muito para chegar na temperatura, ou nunca chega
→ Dobre o valor de P

**I muito alto →** temperatura ultrapassa o alvo e demora para estabilizar
→ Reduza I

**D muito alto →** resposta lenta, parece "travado"
→ Reduza D

---

## Exemplo de configuração para 20L com resistência de 2000W

```
P = 117.0
I = 0.33
D = 41.58
Max output % = 100
Boil threshold = 99
```

---

## Solução de problemas

**Temperatura não sobe:**
- Verifique se o actor (relé da resistência) está configurado no kettle
- Confirme que o kettle está em modo automático (botão ligado na dashboard)

**Temperatura oscila muito:**
- Reduza o valor de P
- Aumente levemente o valor de D

**Temperatura para antes de chegar no alvo:**
- Aumente o valor de I gradualmente

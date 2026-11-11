# PIDAutoTune

Calcula automaticamente os parâmetros ideais de P, I e D para o seu sistema usando o método de **Ziegler-Nichols por oscilação forçada** (relay feedback). Você não precisa saber nada de teoria de controle — o plugin faz tudo sozinho.

---

## Como funciona

O AutoTune aplica pulsos de potência no kettle e observa as oscilações de temperatura. Com base na amplitude e período dessas oscilações, calcula os valores de P, I e D que darão ao seu sistema a resposta mais precisa possível.

**Duração típica:** 30 a 90 minutos, dependendo do volume de água e da potência da resistência.

---

## Pré-requisitos

Nenhuma dependência extra. O plugin está incluído no repositório.

---

## Passo a passo

### 1. Preparar o sistema

- Encha o kettle com a quantidade de água que você usa normalmente (mesmo volume que nas receitas)
- Certifique-se de que o sensor de temperatura está posicionado corretamente
- O kettle precisa estar com o actor (resistência) configurado

### 2. Configurar o kettle com PIDAutoTune

1. Acesse o CraftBeerPi: `http://<ip-do-rpi>:5000`
2. Vá em **System → Kettles**
3. Edite o kettle desejado
4. No campo **Logic**, selecione `PIDAutoTune`
5. Configure os parâmetros:

| Parâmetro | Descrição | Valor recomendado |
|-----------|-----------|-------------------|
| `output step %` | Pulso de potência aplicado | `100` |
| `max. output %` | Potência máxima | `100` |
| `lookback seconds` | Janela de observação de picos | `30` |

6. Defina a **temperatura alvo** do kettle para a temperatura de mosturação que você usa (ex: 65°C)
7. Clique em **Save**

### 3. Iniciar o AutoTune

1. Na dashboard, ligue o modo automático do kettle (botão ao lado do kettle)
2. Uma notificação verde aparecerá: **"AutoTune In Progress — Do not turn off Auto mode"**
3. **Não desligue o modo automático** enquanto o processo estiver rodando

### 4. Aguardar o resultado

O AutoTune vai:
1. Ligar a resistência no potência máxima
2. Observar a temperatura subir e ultrapassar o alvo
3. Desligar a resistência
4. Observar a temperatura cair abaixo do alvo
5. Repetir isso até detectar oscilações estáveis (mínimo 4 picos)

Quando terminar, aparecerão notificações com os valores calculados:

```
✔ AutoTune Complete — PID AutoTune was successful
ℹ AutoTune P Value: 117.3
ℹ AutoTune I Value: 0.33
ℹ AutoTune D Value: 41.58
```

> Os valores são calculados pela regra `brewing` (Ziegler-Nichols modificado para cervejaria).

### 5. Aplicar os valores no PIDBoil

1. Anote os valores de P, I e D exibidos nas notificações
2. Vá em **System → Kettles**
3. Troque o **Logic** do kettle de `PIDAutoTune` para `PIDBoil`
4. Insira os valores de P, I, D obtidos
5. Clique em **Save**

---

## Regras de sintonização disponíveis

O AutoTune calcula os parâmetros para múltiplas regras. Os valores notificados são da regra `brewing`, mas você pode ver todas no log:

```bash
cat /home/otavio/craftbeerpi3/logs/autotune.log
```

| Regra | Comportamento |
|-------|--------------|
| `ziegler-nichols` | Resposta rápida, pode oscilar levemente |
| `tyreus-luyben` | Mais conservador, menos overshoot |
| `brewing` | Equilibrado para cervejaria (recomendado) |
| `no-overshoot` | Nunca ultrapassa o alvo, mas resposta mais lenta |
| `some-overshoot` | Overshoot pequeno permitido, resposta mais rápida |

---

## Solução de problemas

**"AutoTune Failed":**
- O sistema não conseguiu detectar oscilações estáveis em 20 ciclos
- Causas comuns: volume de água muito pequeno, potência da resistência muito alta em relação ao volume, sensor mal posicionado
- Tente aumentar o valor de `lookback seconds` para 60

**O AutoTune demora muito:**
- Normal para volumes grandes (>30L) ou resistências de baixa potência
- Não interrompa — deixe completar

**Não aparecem notificações com os valores:**
- Verifique se o AutoTune completou (`state == succeeded` no log)
- Veja o log: `cat /home/otavio/craftbeerpi3/logs/autotune.log`

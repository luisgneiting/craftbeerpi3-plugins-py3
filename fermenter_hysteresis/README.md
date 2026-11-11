# fermenter_hysteresis

Controlador de temperatura para fermentadores com lógica de **histerese**. Controla independentemente um aquecedor e um resfriador para manter a temperatura de fermentação dentro de uma faixa precisa.

---

## Como funciona

A histerese evita que o equipamento ligue e desligue o tempo todo (efeito "bater"). Em vez de agir exatamente na temperatura alvo, o controlador usa offsets para definir quando ligar e desligar cada equipamento:

```
Alvo: 20°C

Aquecedor liga  → temperatura < (alvo - heater_on_offset)   → ex: < 19.5°C
Aquecedor desliga → temperatura > (alvo - heater_off_offset) → ex: > 20.0°C

Resfriador liga  → temperatura > (alvo + cooler_on_offset)   → ex: > 20.5°C
Resfriador desliga → temperatura < (alvo + cooler_off_offset) → ex: < 20.0°C
```

---

## Pré-requisitos

Nenhuma dependência extra. O plugin está incluído no repositório.

**Equipamentos necessários:**
- 1 sensor de temperatura no fermentador
- 1 actor para o aquecedor (ex: manta ou resistência aquática)
- 1 actor para o resfriador (ex: compressor de geladeira adaptada ou módulo Peltier)
  - O resfriador é **opcional** — pode usar só o aquecedor

---

## Passo a passo

### 1. Configurar os actors

Antes de configurar o fermentador, crie os actors necessários:

1. Vá em **System → Actors**
2. Adicione um actor para o **aquecedor** (ex: `GPIOSimple`, pino conectado à manta)
3. Adicione um actor para o **resfriador** (ex: `GPIOSimple`, pino conectado ao compressor)
4. Anote os nomes de ambos

### 2. Configurar o fermentador

1. Vá em **System → Fermenters**
2. Clique em **+** para adicionar um fermentador (ou edite um existente)
3. Preencha os campos:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `Name` | Nome do fermentador | `Fermentador 1` |
| `Sensor` | Sensor de temperatura dentro do fermentador | `SENSOR 1` |
| `Heater` | Actor do aquecedor | `RELE 3 AQUECEDOR` |
| `Cooler` | Actor do resfriador (opcional) | `RELE 4 RESFRIADOR` |
| `Logic` | Selecione `FermenterHysteresis` | — |

4. Configure os parâmetros de histerese:

| Parâmetro | Descrição | Valor típico |
|-----------|-----------|--------------|
| `Heater On Offset` | Quantos graus abaixo do alvo para ligar o aquecedor | `0.5` |
| `Heater Off Offset` | Quantos graus abaixo do alvo para desligar o aquecedor | `0.0` |
| `Cooler On Offset` | Quantos graus acima do alvo para ligar o resfriador | `0.5` |
| `Cooler Off Offset` | Quantos graus acima do alvo para desligar o resfriador | `0.0` |

5. Clique em **Save**

### 3. Definir a temperatura alvo e ligar

1. Na dashboard, localize o card do fermentador
2. Clique no ícone de temperatura e defina o alvo (ex: `20`)
3. Clique no botão para ligar o modo automático
4. O controlador começa a monitorar e agir

---

## Exemplo prático — fermentação de Ale a 20°C

```
Temperatura alvo: 20°C
Heater On Offset:  0.5  → liga aquecedor se temp < 19.5°C
Heater Off Offset: 0.0  → desliga aquecedor quando temp = 20.0°C
Cooler On Offset:  0.5  → liga resfriador se temp > 20.5°C
Cooler Off Offset: 0.0  → desliga resfriador quando temp = 20.0°C
```

Com essa configuração, a temperatura fica entre **19.5°C e 20.5°C** — tolerância de ±0.5°C, suficiente para a maioria das leveduras.

---

## Sem resfriador (só aquecimento)

Se você não tem resfriador, deixe o campo **Cooler** vazio. O controlador vai funcionar normalmente só com o aquecedor — útil em ambientes frios.

---

## Solução de problemas

**O aquecedor não liga:**
- Verifique se o fermentador está em modo automático (ícone ligado)
- Confirme que o actor está associado corretamente ao campo `Heater`
- Teste o actor manualmente em **System → Actors**

**A temperatura oscila muito:**
- Aumente os offsets de On/Off para criar uma faixa maior de histerese
- Ex: `Heater On Offset: 1.0`, `Heater Off Offset: 0.5`

**Aquecedor e resfriador ligam ao mesmo tempo:**
- Isso não deve acontecer na lógica normal
- Verifique se os offsets de aquecedor e resfriador não se sobrepõem

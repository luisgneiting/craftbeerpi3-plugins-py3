# gpio_actor

Controla pinos GPIO do Raspberry Pi para ligar e desligar equipamentos (resistências, bombas, válvulas) e suporta PWM para controle de potência variável.

---

## Tipos de actor disponíveis

| Tipo | Descrição |
|------|-----------|
| **GPIOSimple** | Liga/desliga digital (on/off) |
| **GPIOPWM** | PWM — controle de potência de 0 a 100% |
| **RelayBoard** | Lógica invertida para placas de relé ativo-baixo |
| **Dummy** | Actor simulado, não aciona nenhum pino (para testes) |

---

## Pré-requisitos

### 1. Instalar rpi-lgpio

No Raspberry Pi OS 13 (Trixie), a biblioteca `RPi.GPIO` foi removida. O substituto é o `rpi-lgpio`:

```bash
pip3 install rpi-lgpio --break-system-packages
```

Verifique se instalou corretamente:

```bash
python3 -c "import RPi.GPIO; print('OK')"
```

### 2. Verificar permissão de GPIO

O serviço do CraftBeerPi roda como `root`, então já tem acesso ao GPIO. Se rodar como outro usuário, adicione-o ao grupo `gpio`:

```bash
sudo usermod -aG gpio SEU_USUARIO
```

---

## Como configurar na interface web

1. Acesse o CraftBeerPi no navegador: `http://<ip-do-rpi>:5000`
2. Vá em **System → Actors**
3. Clique em **+** para adicionar um novo actor
4. Escolha o tipo (ex: `GPIOSimple`)
5. Preencha os campos e clique em **Save**

---

## GPIOSimple — Liga/Desliga

**Quando usar:** resistência de aquecimento, bomba, válvula solenóide.

**Parâmetros:**

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `GPIO` | Número do pino (numeração BCM) | `17` |

**Numeração BCM dos pinos mais comuns:**

```
Pino físico 11 → GPIO 17
Pino físico 13 → GPIO 27
Pino físico 15 → GPIO 22
Pino físico 29 → GPIO 5
Pino físico 31 → GPIO 6
Pino físico 33 → GPIO 13
Pino físico 35 → GPIO 19
Pino físico 37 → GPIO 26
```

> **Dica:** Use `pinout` no terminal do RPi para ver o mapa completo de pinos.

---

## GPIOPWM — Controle de potência variável

**Quando usar:** dimmer de resistência, controle de velocidade de motor DC.

**Parâmetros:**

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `GPIO` | Número do pino BCM | `18` |
| `Frequency` | Frequência PWM em Hz | `50` |

> **Atenção:** PWM por software no RPi pode ser instável em alguns pinos. Para PWM de hardware, use os pinos GPIO 12, 13, 18 ou 19.

---

## RelayBoard — Placa de relé ativo-baixo

**Quando usar:** placas de relé chinesas baratas que ativam com sinal LOW (0V) em vez de HIGH (3.3V).

**Parâmetros:**

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `GPIO` | Número do pino BCM | `17` |

A lógica é invertida internamente: o pino vai para LOW quando o actor é ligado, e HIGH quando desligado.

---

## Dummy — Actor de teste

Não aciona nenhum pino físico. Útil para testar fluxos de receitas sem equipamento conectado.

Sem parâmetros.

---

## Solução de problemas

**O actor não liga:**
- Confirme que `rpi-lgpio` está instalado: `python3 -c "import RPi.GPIO"`
- Verifique o número do pino GPIO (BCM, não o número físico)
- Teste o pino manualmente: `python3 -c "import RPi.GPIO as G; G.setmode(G.BCM); G.setup(17, G.OUT); G.output(17, G.HIGH)"`

**Erro `RuntimeError: This channel is already in use`:**
- Outro processo está usando o pino. Reinicie o serviço: `sudo systemctl restart craftbeerpi`

**Placa de relé liga invertida:**
- Use o tipo `RelayBoard` em vez de `GPIOSimple`

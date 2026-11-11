# AmazonAlexaPlugin

Controle o CraftBeerPi3 por voz usando a **Amazon Alexa**. Pergunte a temperatura, o passo atual, ligue ou desligue equipamentos — tudo sem tocar no celular.

---

## Comandos disponíveis

| Você diz | O que acontece |
|----------|----------------|
| *"Alexa, abre CraftBeerPi"* | Abre a skill |
| *"Me dê um update"* | Informa o passo atual e as temperaturas de todos os kettles |
| *"Temperatura do sensor [nome]"* | Lê o valor do sensor pelo nome |
| *"Temperatura do kettle [nome]"* | Lê a temperatura atual do kettle |
| *"Liga [nome do actor]"* | Liga o actor com aquele nome |
| *"Desliga [nome do actor]"* | Desliga o actor com aquele nome |
| *"Qual é o passo atual?"* | Informa o nome do passo em execução |
| *"Tchau"* | Encerra a sessão |

> Os nomes dos sensores, kettles e actors são os que você cadastrou no CraftBeerPi (ex: se o kettle se chama "Panela Principal", diga "temperatura do kettle panela principal").

---

## Requisitos

- Conta Amazon (gratuita) em developer.amazon.com
- Raspberry Pi com CraftBeerPi3 rodando
- Dispositivo Alexa (Echo, Echo Dot, etc.) **ou** o app Alexa no celular
- Acesso HTTPS ao RPi (via ngrok — explicado abaixo)

---

## Passo a passo completo

### Parte 1 — Instalar as dependências no RPi

```bash
pip install flask-ask-sdk ask-sdk-core --break-system-packages
```

Verifique:

```bash
python3 -c "from flask_ask_sdk.skill_adapter import SkillAdapter; print('OK')"
```

---

### Parte 2 — Instalar e configurar o ngrok

O ngrok cria um túnel HTTPS público para o seu RPi. A Amazon precisa de HTTPS para chamar o endpoint da skill.

**1. Criar conta gratuita no ngrok:**

Acesse [https://ngrok.com](https://ngrok.com) e crie uma conta gratuita.

**2. Instalar o ngrok no RPi:**

```bash
# Baixar
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Ou instalar manualmente:
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz
tar xvzf ngrok-v3-stable-linux-arm.tgz
sudo mv ngrok /usr/local/bin/
```

**3. Autenticar o ngrok:**

No painel do ngrok (ngrok.com → Your Authtoken), copie seu token e rode:

```bash
ngrok config add-authtoken SEU_TOKEN_AQUI
```

**4. Iniciar o túnel:**

```bash
ngrok http 5000
```

A saída será algo como:

```
Forwarding  https://a1b2c3d4.ngrok-free.app -> http://localhost:5000
```

**Anote essa URL HTTPS** — você vai usar ela no próximo passo.

> **Importante:** A URL gratuita muda toda vez que você reinicia o ngrok. Se isso for um problema, considere o plano pago do ngrok (~$8/mês) ou o Cloudflare Tunnel (gratuito com URL fixa).

---

### Parte 3 — Criar a Alexa Skill

**1. Acesse o Amazon Developer Console:**

[https://developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask)

Faça login com sua conta Amazon.

**2. Crie uma nova skill:**

- Clique em **Create Skill**
- Nome: `CraftBeerPi` (ou o nome que preferir — é o que você vai dizer para a Alexa)
- Idioma: escolha o seu idioma (Português - BR ou English)
- Modelo: **Custom**
- Método de hospedagem: **Provision your own**
- Clique em **Create skill**

**3. Configure o endpoint:**

- No menu lateral, clique em **Endpoint**
- Selecione **HTTPS**
- No campo **Default Region**, cole a URL do ngrok + `/alexa`:
  ```
  https://a1b2c3d4.ngrok-free.app/alexa
  ```
- Em **SSL Certificate Type**, selecione: `My development endpoint is a sub-domain of a domain that has a wildcard certificate from a certificate authority`
- Clique em **Save endpoints**

**4. Configure o Interaction Model (intents):**

No menu lateral, clique em **Interaction Model → Intents** e adicione os seguintes intents:

| Intent | Slots | Exemplo de utterance |
|--------|-------|----------------------|
| `Update` | — | "me dê um update", "como está a cerveja" |
| `SensorIntent` | `Sensor` (tipo: AMAZON.SearchQuery) | "temperatura do sensor {Sensor}" |
| `KettleIntent` | `K` (tipo: AMAZON.SearchQuery) | "temperatura do kettle {K}" |
| `ActorIntent` | `Actor` (tipo: AMAZON.SearchQuery) | "liga {Actor}", "desliga {Actor}" |
| `StepIntent` | — | "qual é o passo atual", "que passo está rodando" |
| `Goodbye` | — | "tchau", "até logo" |

Para cada intent:
1. Clique em **Add Intent**
2. Digite o nome exato (ex: `Update`)
3. Adicione as frases de exemplo em **Sample Utterances**
4. Se tiver slot, adicione em **Intent Slots**

**5. Build o modelo:**

Clique em **Save Model** e depois em **Build Model**. Aguarde a mensagem "Build Successful".

**6. Copie o Skill ID:**

No menu lateral, vá em **Endpoint** ou na tela inicial da skill. O Skill ID tem o formato:
```
amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### Parte 4 — Configurar o Skill ID no RPi

Abra o arquivo do plugin:

```bash
sudo nano /home/otavio/craftbeerpi3/modules/plugins/AmazonAlexaPlugin/__init__.py
```

Localize a linha:

```python
SKILL_ID = os.environ.get("ALEXA_SKILL_ID", "amzn1.ask.skill.YOUR_SKILL_ID_HERE")
```

Substitua `YOUR_SKILL_ID_HERE` pelo seu Skill ID real. Ou, em vez de editar o arquivo, defina a variável de ambiente:

```bash
# Adicionar ao final de /etc/environment para persistir entre reinicializações:
echo 'ALEXA_SKILL_ID="amzn1.ask.skill.SEU_ID_AQUI"' | sudo tee -a /etc/environment

# Recarregar:
sudo systemctl daemon-reload
sudo systemctl restart craftbeerpi
```

---

### Parte 5 — Testar

**1. Certifique-se que tudo está rodando:**

```bash
# CraftBeerPi:
sudo systemctl status craftbeerpi

# ngrok (em outro terminal ou em background):
ngrok http 5000 &
```

**2. No Amazon Developer Console:**

- Vá em **Test** (menu superior)
- Ative o modo de teste: **Skill testing is enabled in: Development**
- Digite ou fale: `abre craftbeerpi` (ou o nome que você deu à skill)
- Você deve receber: *"Welcome to CraftBeerPi Alexa Plugin"*

**3. No dispositivo Alexa físico:**

Diga: *"Alexa, abre CraftBeerPi"*

Se não reconhecer, diga: *"Alexa, fala com CraftBeerPi"*

---

## Manter o ngrok rodando

Para o ngrok não fechar quando você sair do terminal, rode como serviço:

```bash
# Criar serviço systemd para o ngrok:
sudo tee /etc/systemd/system/ngrok.service > /dev/null <<EOF
[Unit]
Description=ngrok tunnel for CraftBeerPi
After=network.target craftbeerpi.service

[Service]
ExecStart=/usr/local/bin/ngrok http 5000 --log=stdout
Restart=on-failure
User=otavio

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ngrok
sudo systemctl start ngrok
```

Verificar URL ativa:

```bash
curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; t=json.load(sys.stdin)['tunnels']; print(t[0]['public_url'] if t else 'ngrok não está rodando')"
```

> Lembre-se: na versão gratuita a URL muda a cada reinicialização do ngrok. Após reiniciar, atualize o endpoint no Amazon Developer Console.

---

## Solução de problemas

**A Alexa diz "não encontrei essa skill":**
- O nome que você fala deve ser exatamente o nome da skill no console
- Aguarde alguns minutos após o build do modelo

**A Alexa diz "houve um problema com a skill":**
- O endpoint não está respondendo — verifique se o ngrok está rodando
- Verifique se o CraftBeerPi está rodando: `sudo systemctl status craftbeerpi`
- Veja os logs: `sudo journalctl -u craftbeerpi -f`

**Erro de certificado SSL:**
- Certifique-se de selecionar a opção correta de certificado no Amazon Console (wildcard)

**A URL do ngrok mudou:**
- Atualize o endpoint no Amazon Developer Console → Endpoint → HTTPS

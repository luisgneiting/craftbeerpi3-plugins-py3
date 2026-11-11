# craftbeerpi3-plugins-py3

Plugins para o [CraftBeerPi3](https://github.com/Manuel83/craftbeerpi3), atualizados para **Python 3.13 / Flask 3** no **Raspberry Pi OS 13 (Trixie)**.

Compatível com o fork [`luisgneiting/craftbeerpi3`](https://github.com/luisgneiting/craftbeerpi3) (branch `python3-flask3-compat`).

---

## Plugins disponíveis

| Plugin | Descrição | Documentação |
|--------|-----------|--------------|
| `gpio_actor` | Controle de pinos GPIO (relés, PWM) | [→ README](gpio_actor/README.md) |
| `PIDBoil` | Controlador PID com modo fervura | [→ README](PIDBoil/README.md) |
| `PIDAutoTune` | Cálculo automático de parâmetros PID | [→ README](PIDAutoTune/README.md) |
| `fermenter_hysteresis` | Controle de fermentação por histerese | [→ README](fermenter_hysteresis/README.md) |
| `AmazonAlexaPlugin` | Controle por voz com Amazon Alexa | [→ README](AmazonAlexaPlugin/README.md) |

---

## Instalação rápida

Clone este repositório dentro da pasta `modules/plugins` do CraftBeerPi3:

```bash
cd /home/otavio/craftbeerpi3/modules
git clone https://github.com/luisgneiting/craftbeerpi3-plugins-py3 plugins
```

> **Atenção:** isso substitui toda a pasta `plugins/`. Faça backup se tiver plugins customizados.

Reinicie o serviço:

```bash
sudo systemctl restart craftbeerpi
```

Para atualizar no futuro:

```bash
cd /home/otavio/craftbeerpi3/modules/plugins
git pull
sudo systemctl restart craftbeerpi
```

---

## Requisitos do sistema

- Raspberry Pi OS 13 (Trixie) ou superior
- Python 3.11+
- Flask 3.x
- CraftBeerPi3 fork: [`luisgneiting/craftbeerpi3`](https://github.com/luisgneiting/craftbeerpi3), branch `python3-flask3-compat`

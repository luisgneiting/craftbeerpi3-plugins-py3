# -*- coding: utf-8 -*-
# AmazonAlexaPlugin — rewritten for flask-ask-sdk (Flask 3 / Python 3 compatible)
#
# Quick setup:
#   1. Install: pip install flask-ask-sdk ask-sdk-core --break-system-packages
#   2. Start ngrok: ngrok http 5000
#   3. Register skill at https://developer.amazon.com/alexa/console/ask
#      - Endpoint: https://<ngrok-url>/alexa
#      - Import interaction model from: http://<rpi-ip>:5000/api/alexa/interaction_model
#   4. Set ALEXA_SKILL_ID env var (or edit SKILL_ID below)
#   5. Test with: "Alexa, open CraftBeerPi"

import os
import json

try:
    from ask_sdk_core.skill_builder import SkillBuilder
    from ask_sdk_core.dispatch_components import AbstractRequestHandler
    from ask_sdk_core.utils import is_request_type, is_intent_name
    from ask_sdk_model.ui import SimpleCard
    from flask_ask_sdk.skill_adapter import SkillAdapter
    from flask import Blueprint, jsonify
    _ASK_SDK_AVAILABLE = True
except ImportError:
    _ASK_SDK_AVAILABLE = False

if not _ASK_SDK_AVAILABLE:
    pass  # flask-ask-sdk not installed; plugin disabled silently
else:
    from modules import app, cbpi

    SKILL_ID = os.environ.get("ALEXA_SKILL_ID", "amzn1.ask.skill.YOUR_SKILL_ID_HERE")

    if SKILL_ID == "amzn1.ask.skill.YOUR_SKILL_ID_HERE":
        app.logger.warning(
            "AmazonAlexaPlugin: ALEXA_SKILL_ID not configured. "
            "Set the ALEXA_SKILL_ID environment variable or edit the plugin."
        )

    sb = SkillBuilder()

    def _get_slot(handler_input, slot_name):
        try:
            slots = handler_input.request_envelope.request.intent.slots
            slot = slots.get(slot_name)
            return slot.value.strip().lower() if slot and slot.value else None
        except Exception:
            return None

    def _speak(handler_input, text, card_title="CraftBeerPi"):
        return (handler_input.response_builder
                .speak(text)
                .ask("Any further question?")
                .set_card(SimpleCard(card_title, text))
                .response)

    # ── Launch ────────────────────────────────────────────────────────────────

    class LaunchRequestHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_request_type("LaunchRequest")(handler_input)

        def handle(self, handler_input):
            text = "Welcome to CraftBeerPi. You can ask for an update, sensor temperatures, kettle temperatures, or control your actors."
            return _speak(handler_input, text, "CraftBeerPi")

    # ── Update (general status) ───────────────────────────────────────────────

    class UpdateIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("Update")(handler_input)

        def handle(self, handler_input):
            s = cbpi.cache.get("active_step")
            text = "Here is your update. "
            if s is not None:
                text += "The current step is %s. " % s.name
            else:
                text += "There is no brewing process running. "
            text += "Kettle temperatures: "
            for value in cbpi.cache.get("kettle", {}).values():
                current = cbpi.get_sensor_value(value.sensor)
                text += "%s: target %s, current %s. " % (value.name, value.target_temp, current)
            return _speak(handler_input, text, "CBPi Update")

    # ── Sensor ────────────────────────────────────────────────────────────────

    class SensorIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("SensorIntent")(handler_input)

        def handle(self, handler_input):
            sensor_name = _get_slot(handler_input, "Sensor")
            if sensor_name is None:
                return _speak(handler_input, "Which sensor do you want to check?", "Sensor")
            for value in cbpi.cache.get("sensors", {}).values():
                if value.name.strip().lower() == sensor_name:
                    v = cbpi.get_sensor_value(value.id)
                    unit = value.instance.get_unit() if value.instance else ""
                    text = "The sensor %s reads %s %s" % (value.name, v, unit)
                    return _speak(handler_input, text, "Sensor")
            text = "I could not find sensor %s." % sensor_name
            return _speak(handler_input, text, "Sensor")

    # ── Kettle ────────────────────────────────────────────────────────────────

    class KettleIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("KettleIntent")(handler_input)

        def handle(self, handler_input):
            kettle_name = _get_slot(handler_input, "K")
            if kettle_name is None:
                return _speak(handler_input, "Which kettle do you want to check?", "Kettle")
            for value in cbpi.cache.get("kettle", {}).values():
                if value.name.strip().lower() == kettle_name:
                    v = cbpi.get_sensor_value(value.sensor)
                    s = cbpi.cache.get("sensors", {}).get(int(value.sensor)) if value.sensor else None
                    unit = s.instance.get_unit() if s and s.instance else ""
                    text = "%s is at %s %s, target is %s" % (value.name, v, unit, value.target_temp)
                    return _speak(handler_input, text, "Kettle")
            text = "I could not find kettle %s." % kettle_name
            return _speak(handler_input, text, "Kettle")

    # ── Actor on ──────────────────────────────────────────────────────────────

    class ActorOnIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("ActorOnIntent")(handler_input)

        def handle(self, handler_input):
            actor_name = _get_slot(handler_input, "Actor")
            if actor_name is None:
                return _speak(handler_input, "Which actor do you want to turn on?", "Actor")
            for value in cbpi.cache.get("actors", {}).values():
                if value.name.strip().lower() == actor_name:
                    cbpi.switch_actor_on(value.id)
                    text = "OK, I turned %s on." % value.name
                    return _speak(handler_input, text, "Actor")
            text = "I could not find actor %s." % actor_name
            return _speak(handler_input, text, "Actor")

    # ── Actor off ─────────────────────────────────────────────────────────────

    class ActorOffIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("ActorOffIntent")(handler_input)

        def handle(self, handler_input):
            actor_name = _get_slot(handler_input, "Actor")
            if actor_name is None:
                return _speak(handler_input, "Which actor do you want to turn off?", "Actor")
            for value in cbpi.cache.get("actors", {}).values():
                if value.name.strip().lower() == actor_name:
                    cbpi.switch_actor_off(value.id)
                    text = "OK, I turned %s off." % value.name
                    return _speak(handler_input, text, "Actor")
            text = "I could not find actor %s." % actor_name
            return _speak(handler_input, text, "Actor")

    # ── Step ──────────────────────────────────────────────────────────────────

    class StepIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("StepIntent")(handler_input)

        def handle(self, handler_input):
            s = cbpi.cache.get("active_step")
            if s is not None:
                text = "The current brewing step is %s." % s.name
            else:
                text = "There is no brewing process running."
            return _speak(handler_input, text, "Step")

    # ── Goodbye ───────────────────────────────────────────────────────────────

    class GoodbyeIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("Goodbye")(handler_input)

        def handle(self, handler_input):
            text = "Goodbye! Cheers and happy brewing!"
            return (handler_input.response_builder
                    .speak(text)
                    .set_card(SimpleCard("Goodbye", text))
                    .response)

    # ── Session ended ─────────────────────────────────────────────────────────

    class SessionEndedRequestHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_request_type("SessionEndedRequest")(handler_input)

        def handle(self, handler_input):
            return handler_input.response_builder.response

    # ── Register handlers and wire up Flask route ─────────────────────────────

    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(UpdateIntentHandler())
    sb.add_request_handler(SensorIntentHandler())
    sb.add_request_handler(KettleIntentHandler())
    sb.add_request_handler(ActorOnIntentHandler())
    sb.add_request_handler(ActorOffIntentHandler())
    sb.add_request_handler(StepIntentHandler())
    sb.add_request_handler(GoodbyeIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())

    skill_adapter = SkillAdapter(skill=sb.create(), skill_id=SKILL_ID)
    skill_adapter.register(app, route="/alexa")

    # ── Helper endpoints ──────────────────────────────────────────────────────

    alexa_bp = Blueprint("alexa_helper", __name__)

    @alexa_bp.route("/api/alexa/status", methods=["GET"])
    def alexa_status():
        return jsonify({
            "sdk_available": True,
            "skill_id_configured": SKILL_ID != "amzn1.ask.skill.YOUR_SKILL_ID_HERE",
            "skill_id": SKILL_ID,
            "endpoint": "/alexa",
        })

    @alexa_bp.route("/api/alexa/interaction_model", methods=["GET"])
    def alexa_interaction_model():
        """
        Returns a ready-to-import Alexa Interaction Model JSON.
        In the Amazon Developer Console: Interaction Model → JSON Editor → Import.
        """
        actors = [v.name for v in cbpi.cache.get("actors", {}).values()]
        sensors = [v.name for v in cbpi.cache.get("sensors", {}).values()]
        kettles = [v.name for v in cbpi.cache.get("kettle", {}).values()]

        model = {
            "interactionModel": {
                "languageModel": {
                    "invocationName": "craftbeerpi",
                    "intents": [
                        {
                            "name": "AMAZON.CancelIntent",
                            "samples": []
                        },
                        {
                            "name": "AMAZON.HelpIntent",
                            "samples": []
                        },
                        {
                            "name": "AMAZON.StopIntent",
                            "samples": []
                        },
                        {
                            "name": "Update",
                            "slots": [],
                            "samples": [
                                "give me an update",
                                "how is the beer",
                                "what is the status",
                                "status update",
                                "brewing update",
                                "how is everything going",
                                "me dê um update",
                                "como está a cerveja",
                                "qual é o status",
                            ]
                        },
                        {
                            "name": "SensorIntent",
                            "slots": [
                                {"name": "Sensor", "type": "SensorNameType"}
                            ],
                            "samples": [
                                "sensor {Sensor} temperature",
                                "what is the temperature of sensor {Sensor}",
                                "temperatura do sensor {Sensor}",
                                "sensor {Sensor}",
                            ]
                        },
                        {
                            "name": "KettleIntent",
                            "slots": [
                                {"name": "K", "type": "KettleNameType"}
                            ],
                            "samples": [
                                "kettle {K} temperature",
                                "what is the temperature of {K}",
                                "temperatura do kettle {K}",
                                "temperatura da panela {K}",
                                "{K} temperature",
                            ]
                        },
                        {
                            "name": "ActorOnIntent",
                            "slots": [
                                {"name": "Actor", "type": "ActorNameType"}
                            ],
                            "samples": [
                                "turn on {Actor}",
                                "switch on {Actor}",
                                "enable {Actor}",
                                "liga {Actor}",
                                "ligar {Actor}",
                            ]
                        },
                        {
                            "name": "ActorOffIntent",
                            "slots": [
                                {"name": "Actor", "type": "ActorNameType"}
                            ],
                            "samples": [
                                "turn off {Actor}",
                                "switch off {Actor}",
                                "disable {Actor}",
                                "desliga {Actor}",
                                "desligar {Actor}",
                            ]
                        },
                        {
                            "name": "StepIntent",
                            "slots": [],
                            "samples": [
                                "what is the current step",
                                "which step is running",
                                "current brewing step",
                                "qual é o passo atual",
                                "que passo está rodando",
                                "passo atual",
                            ]
                        },
                        {
                            "name": "Goodbye",
                            "slots": [],
                            "samples": [
                                "goodbye",
                                "bye",
                                "stop",
                                "exit",
                                "tchau",
                                "até logo",
                            ]
                        },
                    ],
                    "types": [
                        {
                            "name": "ActorNameType",
                            "values": [{"name": {"value": a}} for a in actors] or [{"name": {"value": "heater"}}]
                        },
                        {
                            "name": "SensorNameType",
                            "values": [{"name": {"value": s}} for s in sensors] or [{"name": {"value": "sensor 1"}}]
                        },
                        {
                            "name": "KettleNameType",
                            "values": [{"name": {"value": k}} for k in kettles] or [{"name": {"value": "main kettle"}}]
                        },
                    ]
                }
            }
        }
        return app.response_class(
            response=json.dumps(model, ensure_ascii=False, indent=2),
            mimetype="application/json"
        )

    app.register_blueprint(alexa_bp)

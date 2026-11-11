# -*- coding: utf-8 -*-
# AmazonAlexaPlugin — rewritten for flask-ask-sdk (Flask 3 / Python 3 compatible)
#
# Setup:
#   1. Register an Alexa Skill at https://developer.amazon.com/alexa/console/ask
#   2. Set the endpoint to: https://<your-rpi-ip-or-domain>/alexa
#      (Amazon requires HTTPS — use ngrok or a reverse proxy with a certificate)
#   3. Copy your Skill ID and set ALEXA_SKILL_ID below (or via environment variable)
#
# Install: pip install flask-ask-sdk ask-sdk-core

import os

try:
    from ask_sdk_core.skill_builder import SkillBuilder
    from ask_sdk_core.dispatch_components import AbstractRequestHandler
    from ask_sdk_core.utils import is_request_type, is_intent_name
    from ask_sdk_model.ui import SimpleCard
    from flask_ask_sdk.skill_adapter import SkillAdapter
    _ASK_SDK_AVAILABLE = True
except ImportError:
    _ASK_SDK_AVAILABLE = False

if not _ASK_SDK_AVAILABLE:
    pass  # flask-ask-sdk not installed; plugin disabled silently
else:
    from modules import app, cbpi

    # Set your Alexa Skill ID here or via the ALEXA_SKILL_ID environment variable.
    SKILL_ID = os.environ.get("ALEXA_SKILL_ID", "amzn1.ask.skill.YOUR_SKILL_ID_HERE")

    sb = SkillBuilder()

    def _get_slot(handler_input, slot_name):
        slots = handler_input.request_envelope.request.intent.slots
        slot = slots.get(slot_name)
        return slot.value if slot and slot.value else None

    # ── Launch ────────────────────────────────────────────────────────────────

    class LaunchRequestHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_request_type("LaunchRequest")(handler_input)

        def handle(self, handler_input):
            text = "Welcome to CraftBeerPi Alexa Plugin"
            return (handler_input.response_builder
                    .speak(text)
                    .ask(text)
                    .set_card(SimpleCard("CraftBeerPi", text))
                    .response)

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
            text += "Now to the brewing kettles. "
            for value in cbpi.cache.get("kettle", {}).values():
                current = cbpi.get_sensor_value(value.sensor)
                text += "%s: target %s, current %s. " % (value.name, value.target_temp, current)
            text += "Any further question?"
            return (handler_input.response_builder
                    .speak(text)
                    .ask(text)
                    .set_card(SimpleCard("CBPi Update", text))
                    .response)

    # ── Sensor ────────────────────────────────────────────────────────────────

    class SensorIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("SensorIntent")(handler_input)

        def handle(self, handler_input):
            sensor_name = _get_slot(handler_input, "Sensor")
            for value in cbpi.cache.get("sensors", {}).values():
                if value.name.lower() == sensor_name:
                    v = cbpi.get_sensor_value(value.id)
                    unit = value.instance.get_unit() if value.instance else ""
                    text = "The sensor temperature is %s %s" % (v, unit)
                    return (handler_input.response_builder
                            .speak(text).ask(text)
                            .set_card(SimpleCard("Sensor Value", text))
                            .response)
            text = "I have not found the sensor %s. Any further question?" % sensor_name
            return (handler_input.response_builder
                    .speak(text).ask(text)
                    .set_card(SimpleCard("Sensor Value", text))
                    .response)

    # ── Kettle ────────────────────────────────────────────────────────────────

    class KettleIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("KettleIntent")(handler_input)

        def handle(self, handler_input):
            kettle_name = _get_slot(handler_input, "K")
            for value in cbpi.cache.get("kettle", {}).values():
                if value.name.lower() == kettle_name:
                    v = cbpi.get_sensor_value(value.sensor)
                    s = cbpi.cache.get("sensors", {}).get(int(value.sensor))
                    unit = s.instance.get_unit() if s and s.instance else ""
                    text = "The kettle temperature of %s is %s %s" % (kettle_name, v, unit)
                    return (handler_input.response_builder
                            .speak(text).ask(text)
                            .set_card(SimpleCard("Kettle Value", text))
                            .response)
            text = "I have not found the kettle %s. Any further question?" % kettle_name
            return (handler_input.response_builder
                    .speak(text).ask(text)
                    .set_card(SimpleCard("Kettle Value", text))
                    .response)

    # ── Actor ─────────────────────────────────────────────────────────────────

    class ActorIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("ActorIntent")(handler_input)

        def handle(self, handler_input):
            actor_name = _get_slot(handler_input, "Actor")
            for value in cbpi.cache.get("actors", {}).values():
                if value.name.lower() == actor_name:
                    if value.state == 1:
                        cbpi.switch_actor_off(value.id)
                        text = "Ok, I switched %s off" % actor_name
                    else:
                        cbpi.switch_actor_on(value.id)
                        text = "Ok, I switched %s on" % actor_name
                    return (handler_input.response_builder
                            .speak(text).ask(text)
                            .set_card(SimpleCard("Actor Toggle", text))
                            .response)
            text = "I have not found the actor %s. Any further question?" % actor_name
            return (handler_input.response_builder
                    .speak(text).ask(text)
                    .set_card(SimpleCard("Actor", text))
                    .response)

    # ── Step ──────────────────────────────────────────────────────────────────

    class StepIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("StepIntent")(handler_input)

        def handle(self, handler_input):
            s = cbpi.cache.get("active_step")
            if s is not None:
                text = "The current step is %s" % s.name
            else:
                text = "There is no brewing process running"
            return (handler_input.response_builder
                    .speak(text).ask(text)
                    .set_card(SimpleCard("Step", text))
                    .response)

    # ── Goodbye ───────────────────────────────────────────────────────────────

    class GoodbyeIntentHandler(AbstractRequestHandler):
        def can_handle(self, handler_input):
            return is_intent_name("Goodbye")(handler_input)

        def handle(self, handler_input):
            text = "OK, don't forget to donate some beer to Manuel! Goodbye"
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
    sb.add_request_handler(ActorIntentHandler())
    sb.add_request_handler(StepIntentHandler())
    sb.add_request_handler(GoodbyeIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())

    skill_adapter = SkillAdapter(
        skill=sb.create(),
        skill_id=SKILL_ID,
    )

    skill_adapter.register(app, route="/alexa")

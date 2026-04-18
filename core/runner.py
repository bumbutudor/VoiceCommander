"""bucla principala partajata: listen -> trigger -> interpret -> execute"""

import sys

from core.voice import Listener
from core.ai import AI
from core.utils import normalize


class Runner:
    def __init__(self, name, trigger, trigger_variants, predicates,
                 context_info, execute_fn, help_text="", wake_word=None,
                 interpreter=None, use_ai=True):
        """
        args:
            name: numele device-ului (ex: "windows", "tello")
            trigger: cuvantul trigger principal (ex: "sistem", "tello")
            trigger_variants: lista de variante trigger (ex: ["sistem", "system"])
            predicates: lista de predicate posibile
            context_info: text cu obiectele disponibile (pentru gemini)
            execute_fn: functia execute(predicate, obj, ai) a device-ului
            help_text: text ajutor afisat la pornire
            wake_word: optional WakeWordDetector. Daca e setat, folosim
                detectorul pentru trigger in loc de cuvant in text.
            interpreter: optional fallback offline cu metoda
                interpret(text, predicates, context_info). Folosit cand
                gemini lipseste sau esueaza (ex: conectat la wifi tello,
                fara internet).
            use_ai: daca False, sare peste gemini si foloseste doar
                interpretorul local (util cu --no-ai).
        """
        self.name = name
        self.trigger = trigger
        self.trigger_variants = trigger_variants
        self.predicates = predicates
        self.context_info = context_info
        self.execute = execute_fn
        self.help_text = help_text
        self.wake_word = wake_word
        self.interpreter = interpreter
        self.use_ai = use_ai

    def find_trigger(self, text):
        """gaseste cuvantul trigger si returneaza restul comenzii"""
        text_norm = normalize(text)
        for trigger in self.trigger_variants:
            if trigger in text_norm:
                idx = text_norm.index(trigger) + len(trigger)
                rest = text_norm[idx:].strip()
                # sterge litere lipite de trigger (sistema->"a", sistemu->"u")
                if rest and rest[0].isalpha() and (len(rest) == 1 or not rest[1].isalpha()):
                    rest = rest[1:].strip()
                rest = rest.lstrip(".,!?;: ")
                return rest
        return None

    def run(self):
        """porneste bucla principala"""
        print(f"voicecommander/{self.name}")
        print("=" * 40)

        # initializare audio + whisper
        try:
            listener = Listener()
        except Exception as e:
            print(f"eroare audio: {e}")
            sys.exit(1)

        # initializare gemini (skip daca use_ai=False)
        ai = None
        if self.use_ai:
            try:
                ai = AI()
            except Exception as e:
                print(f"gemini indisponibil: {e}")

        # calibreaza microfonul
        listener.calibrate()

        if self.help_text:
            print(self.help_text)
        print("-" * 40)

        while True:
            try:
                if self.wake_word is not None:
                    print(f"\n[ascult wake word '{self.trigger}'...]")
                    self.wake_word.wait_for_trigger()
                    print(f"[!] {self.trigger} detectat - astept comanda")
                    text = listener.listen()
                    if not text:
                        print("[?] n-am auzit comanda")
                        continue
                    print(f"[whisper] {text}")
                    command_text = text
                else:
                    print("\n[ascult...]")
                    text = listener.listen()

                    if not text:
                        continue

                    print(f"[whisper] {text}")

                    command_text = self.find_trigger(text)
                    if command_text is None:
                        continue

                print(f"[comanda] {command_text}")

                # interpretare comanda: gemini cu fallback la interpretor local
                predicate, obj = None, None
                if ai:
                    try:
                        predicate, obj = ai.interpret(
                            command_text,
                            self.predicates,
                            self.context_info,
                        )
                    except Exception as e:
                        print(f"[gemini eroare] {e}")
                        predicate, obj = None, None
                    else:
                        if predicate:
                            print(f"[gemini] {predicate}|{obj}")

                if not predicate and self.interpreter is not None:
                    predicate, obj = self.interpreter.interpret(
                        command_text,
                        self.predicates,
                        self.context_info,
                    )
                    if predicate:
                        print(f"[local] {predicate}|{obj}")

                if not predicate and not ai and self.interpreter is None:
                    # fara interpretare disponibila: split naiv
                    words = command_text.split(None, 1)
                    if not words:
                        continue
                    predicate = words[0]
                    obj = words[1] if len(words) > 1 else ""

                if not predicate:
                    print("[?] comanda neclara")
                    continue

                result = self.execute(predicate, obj, ai)
                print(f"[result] {result}")

            except KeyboardInterrupt:
                print("\npa!")
                sys.exit(0)
            except SystemExit:
                sys.exit(0)
            except Exception as e:
                print(f"[eroare] {e}")

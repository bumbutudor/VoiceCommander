"""integrare gemini flash pentru interpretare comenzi si generare cod"""

from google import genai

from core import config


class AI:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY lipseste (seteaza in .env sau variabila de mediu)"
            )
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"

    def generate_code(self, description, language="python", filename=None):
        """genereaza cod pe baza descrierii in limba romana"""
        ctx = f" pentru fisierul {filename}" if filename else ""
        prompt = (
            f"genereaza cod {language}{ctx} pentru urmatoarea cerinta:\n"
            f"{description}\n\n"
            f"returneaza DOAR codul sursa, fara explicatii, "
            f"fara markdown, fara blocuri ```."
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        code = response.text.strip()
        if code.startswith("```"):
            lines = code.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            code = "\n".join(lines)
        return code

    def interpret(self, text, predicates, context_info=""):
        """interpreteaza o comanda vocala, chiar daca e transcris gresit

        args:
            text: textul transcris de whisper
            predicates: lista de predicate posibile (ex: ["deschide", "inchide", ...])
            context_info: info suplimentar despre obiectele disponibile
        """
        pred_list = ", ".join(predicates)
        prompt = (
            "esti un parser de comenzi vocale in limba romana.\n"
            "textul vine dintr-un sistem de recunoastere vocala "
            "si poate contine erori de transcriere.\n\n"
            f"PREDICATELE posibile: {pred_list}\n\n"
            f"{context_info}\n\n"
            "REGULI:\n"
            "- gaseste cea mai probabila comanda din text\n"
            "- corecteaza greseli de transcriere\n"
            "- daca textul NU contine o comanda clara, raspunde exact: neclar\n\n"
            f"TEXT TRANSCRIS: '{text}'\n\n"
            "raspunde DOAR in formatul: predicat|obiect\n"
            "sau daca nu e clar: neclar\n"
            "NU adauga explicatii."
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        result = response.text.strip().lower()
        if result == "neclar" or "|" not in result:
            return None, None
        parts = result.split("|", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return None, None

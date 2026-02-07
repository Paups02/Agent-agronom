"""Integració amb Google Gemini AI per assessoria conversacional.

Proporciona un assessor agronòmic intel·ligent que respon preguntes
en llenguatge natural sobre cultius, sòls, plagues i pràctiques agrícoles.
"""

import os

GEMINI_SYSTEM_PROMPT = """Ets AgroNom AI, un agrònom professional expert en agricultura mediterrània.

PERFIL PROFESSIONAL:
- Especialista en sòls, fertilització, reg i fitosanitat
- Coneixement profund de cultius mediterranis (horta, fruita, olivera, vinya, cereals)
- Bases científiques: FAO-56, IRTA, MAPA, universitats agràries
- Parles en català/castellà de forma clara i pràctica

COMPORTAMENT:
- Respon sempre amb recomanacions pràctiques i accionables
- Inclou dosis concretes, productes i calendaris quan sigui possible
- Diferencia entre tractaments convencionals i ecològics
- Adverteix sobre riscos ambientals i de seguretat alimentària
- Si no tens prou dades, demana la informació necessària
- Respostes concises però completes (3-6 paràgrafs màxim)

ÀREES D'EXPERTESA:
1. Diagnòstic i correcció de sòls (pH, MO, nutrients, salinitat)
2. Plans de fertilització (mineral i orgànica)
3. Planificació de reg (FAO-56, necessitats hídriques)
4. Identificació i tractament de plagues i malalties
5. Rotació de cultius i cobertes vegetals
6. Agricultura ecològica i sostenible
7. Economia agrària (costos, rendibilitat, ajudes PAC)
"""


def create_gemini_chat(api_key: str | None = None):
    """Crea una sessió de xat amb Gemini."""
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=GEMINI_SYSTEM_PROMPT,
        )
        return model.start_chat(history=[])
    except Exception:
        return None


def ask_gemini(question: str, context: str = "", api_key: str | None = None) -> str:
    """Envia una pregunta a Gemini i retorna la resposta.

    Args:
        question: Pregunta de l'usuari
        context: Context opcional (dades del diagnòstic actual)
        api_key: Clau API de Gemini (opcional, usa env var si no es passa)

    Returns:
        Resposta de Gemini o missatge d'error
    """
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return _offline_response(question)

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=GEMINI_SYSTEM_PROMPT,
        )

        prompt = question
        if context:
            prompt = (
                f"CONTEXT DE LA FINCA DE L'USUARI:\n{context}\n\n"
                f"PREGUNTA: {question}"
            )

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return _offline_response(question, str(e))


def _offline_response(question: str, error: str = "") -> str:
    """Resposta offline quan Gemini no està disponible."""
    q = question.lower()

    # Base de coneixement local per respostes bàsiques
    if any(w in q for w in ["ph", "àcid", "alcalí", "calç"]):
        return (
            "**Correcció de pH del sòl:**\n\n"
            "- **Sòl àcid (pH < 6.0):** Aplicar calç agrícola (CaCO3) a raó de 1-3 t/ha "
            "o dolomita si també manca magnesi. Incorporar a 20-30 cm de profunditat.\n\n"
            "- **Sòl alcalí (pH > 8.0):** Aplicar sofre elemental (300-600 kg/ha) o sulfat de ferro. "
            "L'aportació de matèria orgànica àcida (torba, compost de pi) ajuda a llarg termini.\n\n"
            "- L'efecte de l'encalat triga 2-3 mesos. Repetir anàlisi de sòl cada any.\n\n"
            "*Font: MAPA, Guia de fertilització racional dels cultius*"
        )
    elif any(w in q for w in ["reg", "aigua", "degoteig", "aspersió"]):
        return (
            "**Planificació de reg:**\n\n"
            "El mètode FAO-56 Penman-Monteith calcula les necessitats hídriques:\n"
            "**ETc = ETo × Kc** (evapotranspiració del cultiu)\n\n"
            "- **Degoteig:** Eficiència 85-95%. Reg diari, dosis petites.\n"
            "- **Aspersió:** Eficiència 70-80%. Cada 2-4 dies.\n"
            "- **Inundació:** Eficiència 50-60%. Setmanal.\n\n"
            "En fase de floració/quallat, mai permetre estrès hídric — "
            "redueix un 30-50% la producció.\n\n"
            "*Font: FAO Irrigation & Drainage Paper 56*"
        )
    elif any(w in q for w in ["plaga", "malaltia", "fong", "insecte", "tracta"]):
        return (
            "**Gestió fitosanitària integrada (GIP):**\n\n"
            "1. **Prevenció:** Rotació de cultius, varietats resistents, fauna auxiliar.\n"
            "2. **Monitoratge:** Trampes, inspecció setmanal, llindars d'intervenció.\n"
            "3. **Control biològic:** Bacillus thuringiensis, Trichoderma, depredadors naturals.\n"
            "4. **Control químic:** Últim recurs, alternar matèries actives per evitar resistències.\n\n"
            "Condicions de risc: Humitat >70% + Temperatura 15-25°C = risc de fongs.\n\n"
            "*Font: IRTA, Guies GIP del MAPA*"
        )
    elif any(w in q for w in ["fertil", "nitrogen", "fòsfor", "potassi", "NPK", "abonar"]):
        return (
            "**Principis de fertilització racional:**\n\n"
            "1. **Anàlisi de sòl** prèvia (cada 2-3 anys mínim).\n"
            "2. **Balanç de nutrients:** Aportació = Extraccions + Pèrdues - Reserves.\n"
            "3. **Fraccionament del N:** Mai tot de cop. Repartir en 2-4 aplicacions.\n"
            "4. **P i K en fons:** Incorporar abans de sembrar.\n"
            "5. **Matèria orgànica:** Base de la fertilitat. Mínim 2% MO al sòl.\n\n"
            "Després de lleguminosa, reduir N un 20-30% per fixació biològica residual.\n\n"
            "*Font: MAPA, Codi de bones pràctiques agràries*"
        )
    else:
        msg = (
            "**AgroNom AI — Assessor Agronòmic**\n\n"
            "Puc ajudar-te amb qualsevol qüestió agronòmica:\n"
            "- Diagnòstic i correcció de sòls\n"
            "- Plans de fertilització\n"
            "- Gestió del reg\n"
            "- Identificació de plagues i malalties\n"
            "- Agricultura ecològica\n"
            "- Rendibilitat i costos\n\n"
            "Fes-me una pregunta concreta sobre el teu cultiu!"
        )
        if error:
            msg += (
                f"\n\n*Nota: Gemini AI no disponible ({error}). "
                "Configureu GEMINI_API_KEY per a respostes avançades.*"
            )
        return msg

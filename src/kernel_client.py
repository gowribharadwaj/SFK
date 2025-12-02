import os
import json
from typing import Tuple, Dict
from src.config import settings
from src.utils import get_logger

logger = get_logger("kernel")

try:
    import openai
except Exception:
    openai = None

def _heuristic_extract(message: str, context: dict = None) -> Tuple[str, Dict]:
    # simple heuristics
    import re
    m = message.lower()
    intent = "question"
    if any(w in m for w in ["wrong", "incorrect", "store", "save", "correction", "feedback", "unhelpful", "thanks"]):
        intent = "feedback"

    designation = None
    attr = None
    val = None

    # find designation like 6205 or 6205 n
    d = re.search(r"\b([a-zA-Z]{0,3}\d{3,6}\s?[a-zA-Z]?)\b", message)
    if d:
        designation = d.group(1).strip()

    if "width" in m:
        attr = "width"
    elif "diameter" in m and "bore" not in m:
        attr = "outside diameter"
    elif "bore" in m or "bore diameter" in m:
        attr = "bore diameter"
    elif "weight" in m:
        attr = "product net weight"
    elif "ean" in m:
        attr = "ean code"

    v = re.search(r"(\d+\.?\d*\s*(mm|kg|r/min|rpm)?)", message)
    if v:
        val = v.group(1).strip()

    return intent, {k:v for k,v in {"designation": designation, "attribute": attr, "value": val}.items() if v}

def classify_and_extract(session_id: str, message: str, context: dict = None) -> Tuple[str, Dict]:
    """
    Uses Azure/OpenAI function-calling to extract intent/designation/attribute/value.
    If OpenAI not configured, fall back to heuristics.
    """
    # if openai not available or not configured -> heuristic
    if openai is None:
        logger.info("openai package not installed — using heuristic extractor")
        return _heuristic_extract(message, context)

    # determine config
    use_azure = settings.USE_AZURE
    if use_azure:
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_key = settings.AZURE_OPENAI_KEY
    else:
        openai.api_key = settings.OPENAI_API_KEY

    model = settings.AZURE_OPENAI_DEPLOYMENT if use_azure else settings.OPENAI_MODEL

    system = (
        "You are an extractor for a product Q&A system. "
        "Classify the user's message intent: 'question' or 'feedback' or 'other', "
        "and extract optional fields: designation (e.g., 6205 or 6205 N), attribute (e.g., width, bore diameter), and value (if present). "
        "Return the data only via the function call."
    )
    user = message

    functions = [
        {
            "name": "classify_and_extract",
            "description": "Return intent and optional fields designation, attribute, value.",
            "parameters": {
                "type":"object",
                "properties":{
                    "intent":{"type":"string","enum":["question","feedback","other"]},
                    "designation":{"type":"string"},
                    "attribute":{"type":"string"},
                    "value":{"type":"string"}
                },
                "required":["intent"]
            }
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0,
            functions=functions,
            function_call={"name":"classify_and_extract"}
        )
        msg = response["choices"][0]["message"]
        if "function_call" in msg:
            args_txt = msg["function_call"]["arguments"]
            parsed = json.loads(args_txt)
            intent = parsed.get("intent","other")
            extraction = {k:v for k,v in {
                "designation": parsed.get("designation"),
                "attribute": parsed.get("attribute"),
                "value": parsed.get("value")
            }.items() if v}
            return intent, extraction
    except Exception as e:
        logger.warning("LLM extraction failed (%s) — falling back to heuristics", e)
    return _heuristic_extract(message, context)

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.config import settings
from app.models.scheme import Scheme

logger = logging.getLogger("jansathi.gemini_service")


def detect_language(text: str) -> str:
    """
    Detects language of user message:
    - 'hi': Hindi (Devanagari script)
    - 'hinglish': Hinglish (Romanized Hindi)
    - 'en': English
    """
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    
    hinglish_words = {
        "mujhe", "batao", "karo", "main", "hu", "hai", "yojana", "chahiye", "kaise",
        "subah", "pranam", "dost", "form", "paisa", "madad", "mera", "meri", "hamara",
        "kya", "kaun", "kaha", "se", "ko", "par", "me", "mein", "karne", "rahe", "ho",
        "shukriya", "dhanyawad", "namaskar", "namaste", "bhai", "aavedan", "lagne", "wale",
        "bataiye", "bataen", "batao", "chahiye", "diye", "jana", "padega", "kahan"
    }
    words = re.findall(r'\b\w+\b', text.lower())
    match_count = sum(1 for w in words if w in hinglish_words)
    if match_count >= 1:
        return "hinglish"
    
    return "en"


class GeminiRAGService:
    """
    Multilingual Gemini RAG Service for JanSathi AI acting as an AI Government Case Worker.
    Answers in Hindi, Hinglish, or English based on the user's input language.
    Answers strictly grounded in SQLite-retrieved scheme records with zero hallucination.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("[Gemini RAG] Client initialized successfully.")
            except Exception as err:
                logger.warning(f"[Gemini RAG] Failed to initialize Gemini client: {err}")

    def is_configured(self) -> bool:
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if self.api_key and not self.client:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                pass
        return bool(self.client and self.api_key)

    def generate_grounded_response(
        self,
        user_query: str,
        retrieved_schemes: List[Scheme],
        citizen_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a case-worker grounded response in Hindi, Hinglish, or English using ONLY retrieved schemes.
        """
        lang = language or detect_language(user_query)

        # Format official link & records for context
        formatted_schemes = []
        for s in retrieved_schemes:
            slug = (s.slug or "").strip()
            official_link = f"https://www.myscheme.gov.in/schemes/{slug}" if slug else "N/A"
            formatted_schemes.append({
                "id": s.id,
                "scheme_name": s.scheme_name or s.title_legacy,
                "category": s.schemeCategory or s.category_legacy,
                "details": s.details or s.description_legacy,
                "benefits": s.benefits or "",
                "eligibility": s.eligibility or "",
                "application": s.application or "",
                "documents": s.documents or s.required_documents_legacy,
                "official_link": official_link
            })

        # Mandatory ending lines per language
        if lang == "hi":
            mandatory_end = "क्या आप मुझसे और योजनाओं की तुलना करवाना चाहते हैं, पात्रता विस्तार से जानना चाहते हैं, या सबसे बेहतर योजना चुनने में मदद चाहते हैं?"
            lang_instruction = "CRITICAL: The citizen asked their question in HINDI. You MUST write your entire response in clear, empathetic, respectful Devanagari Hindi (हिंदी)."
        elif lang == "hinglish":
            mandatory_end = "Kya aap mujhse multiple schemes compare karwana chahte hain, eligibility detail me samajhna chahte hain, ya sabse behtar scheme chunne me madad chahte hain?"
            lang_instruction = "CRITICAL: The citizen asked their question in HINGLISH (Hindi written in Roman/Latin script). You MUST write your entire response in natural, conversational Hinglish."
        else:
            mandatory_end = "Would you like me to compare multiple schemes, explain eligibility in detail, or help you choose the best one?"
            lang_instruction = "CRITICAL: Write your response in clear, accessible English."

        system_prompt = (
            "You are JanSathi AI, acting as an empathetic, expert AI Government Case Worker assisting an Indian citizen.\n\n"
            f"{lang_instruction}\n\n"
            "CRITICAL RULES & TONE:\n"
            "1. You answer ONLY using the government scheme records provided to you.\n"
            "2. NEVER invent scheme names, benefits, eligibility, documents, or application steps.\n"
            "3. NEVER dump raw database text or say 'retrieved from database', 'here are database records', or 'search engine'.\n"
            "4. Speak naturally, warmly, and empathetically like a human Government Case Worker guiding a citizen.\n\n"
            "FOR EVERY SCHEME RECOMMENDED, STRUCTURE EXACTLY AS:\n"
            "⭐ Scheme Name: <scheme_name>\n"
            "📌 Why this scheme matches YOU: <personalized eligibility explanation based on user context>\n"
            "💰 Benefits: <benefits summary>\n"
            "📄 Required Documents: <documents>\n"
            "📝 How to Apply (Step by Step): <application guidance>\n"
            "🔗 Official myScheme Link: <official_link>\n"
            "🟢 Eligibility Match: High (or Medium / Low)\n\n"
            "AFTER RECOMMENDING SCHEMES, ALWAYS INCLUDE:\n"
            "📍 Next Steps:\n"
            "1. Keep Aadhaar Card ready.\n"
            "2. Obtain Income Certificate (if applicable).\n"
            "3. Visit nearest Common Service Center (CSC) or apply online on official portal.\n"
            "4. Upload required documents.\n"
            "5. Track application status.\n\n"
            f"ALWAYS FINISH YOUR RESPONSE WITH THIS EXACT MANDATORY LINE:\n"
            f"\"{mandatory_end}\""
        )

        user_content = (
            f"CITIZEN QUERY: {user_query}\n"
            f"TARGET LANGUAGE: {lang.upper()}\n\n"
            f"CITIZEN KNOWN PROFILE CONTEXT: {json.dumps(citizen_context or {}, ensure_ascii=False)}\n\n"
            f"RETRIEVED SCHEME RECORDS ({len(formatted_schemes)} matches):\n"
            f"{json.dumps(formatted_schemes, ensure_ascii=False, indent=2)}"
        )

        # If Gemini is configured, call Gemini API
        if self.is_configured():
            try:
                response = self.client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                    )
                )
                if response and response.text:
                    res_text = response.text.strip()
                    if mandatory_end not in res_text:
                        res_text = f"{res_text}\n\n{mandatory_end}"
                    return {
                        "reply": res_text,
                        "schemes": formatted_schemes
                    }
            except Exception as err:
                logger.error(f"[Gemini RAG] API generation error: {err}")

        # Fallback grounded Case Worker synthesis if API key fails, times out, or hits 429 rate limit
        if lang == "hi":
            reply_lines = [
                "नमस्ते! आपके AI सरकारी केस वर्कर के रूप में, यहाँ आपकी प्रोफाइल से मेल खाने वाली शीर्ष सरकारी योजनाएं हैं:\n"
            ]
            for s in formatted_schemes[:2]:
                reply_lines.append(f"⭐ **{s['scheme_name']}** ({s['category']})")
                reply_lines.append(f"📌 **यह योजना क्यों**: {s['category']} कल्याण के तहत पात्र।")
                if s['benefits']:
                    reply_lines.append(f"💰 **लाभ**: {s['benefits'][:120]}...")
                if s['documents']:
                    reply_lines.append(f"📄 **दस्तावेज**: {s['documents'][:90]}")
                if s['official_link'] != "N/A":
                    reply_lines.append(f"🔗 **लिंक**: {s['official_link']}")
                reply_lines.append("🟢 **पात्रता मेल**: उच्च (High)\n")

            reply_lines.append("📍 **अगले चरण**:\n1. आधार कार्ड एवं आय प्रमाण पत्र तैयार रखें।\n2. निकटतम CSC केंद्र या आधिकारिक पोर्टल पर आवेदन करें।\n")
            reply_lines.append(mandatory_end)

        elif lang == "hinglish":
            reply_lines = [
                "Namaste! Aapke AI Government Case Worker ke roop me, yahan aapki profile se match karne wali top government schemes hain:\n"
            ]
            for s in formatted_schemes[:2]:
                reply_lines.append(f"⭐ **{s['scheme_name']}** ({s['category']})")
                reply_lines.append(f"📌 **Why Match**: Eligible under {s['category']} welfare.")
                if s['benefits']:
                    reply_lines.append(f"💰 **Benefits**: {s['benefits'][:120]}...")
                if s['documents']:
                    reply_lines.append(f"📄 **Documents**: {s['documents'][:90]}")
                if s['official_link'] != "N/A":
                    reply_lines.append(f"🔗 **Link**: {s['official_link']}")
                reply_lines.append("🟢 **Eligibility Match**: High\n")

            reply_lines.append("📍 **Next Steps**:\n1. Keep Aadhaar Card and Income Proof ready.\n2. Apply online or visit nearest CSC center.\n")
            reply_lines.append(mandatory_end)

        else:
            reply_lines = [
                "Namaste! As your AI Government Case Worker, here are the top recommended public welfare schemes matching your profile:\n"
            ]
            for s in formatted_schemes[:2]:
                reply_lines.append(f"⭐ **{s['scheme_name']}** ({s['category']})")
                reply_lines.append(f"📌 **Why Match**: Tailored for your profile under {s['category']} welfare.")
                if s['benefits']:
                    reply_lines.append(f"💰 **Benefits**: {s['benefits'][:120]}...")
                if s['documents']:
                    reply_lines.append(f"📄 **Documents**: {s['documents'][:90]}")
                if s['official_link'] != "N/A":
                    reply_lines.append(f"🔗 **Link**: {s['official_link']}")
                reply_lines.append("🟢 **Eligibility Match**: High\n")

            reply_lines.append("📍 **Next Steps**:\n1. Keep Aadhaar Card and Income Proof ready.\n2. Apply online or visit nearest CSC center.\n")
            reply_lines.append(mandatory_end)

        return {
            "reply": "\n".join(reply_lines),
            "schemes": formatted_schemes
        }


# Singleton instance
gemini_rag_service = GeminiRAGService()

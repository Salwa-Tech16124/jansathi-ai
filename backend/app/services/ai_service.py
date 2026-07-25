import json
import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.scheme import Scheme
from app.services.search_service import search_service
from app.services.gemini_service import gemini_rag_service, detect_language
from app.services.sarvam_service import sarvam_client

logger = logging.getLogger("jansathi.ai_service")

# In-memory Conversation Memory store (indexed by session / citizen_id)
CONVERSATION_MEMORY: Dict[str, Dict[str, Any]] = {}


class AICaseWorkerService:
    """
    Multilingual AI Government Case Worker Service for JanSathi AI.
    
    Supports Hindi (हिंदी), Hinglish, and English:
    - Step 1: Interactive Profile Gathering in detected language.
    - Step 2: Intelligent SQLite Retrieval (Top 5 schemes).
    - Step 3: Multilingual Grounded Gemini RAG Case Worker Explanation with Next Steps.
    - Conversation Memory: Preserves user profile attributes across chat turns.
    - Sarvam AI Routing: Handles general greetings and non-government banter in Hindi/Hinglish/English.
    """

    def analyze_and_respond(self, message: str, db: Session, session_id: str = "default") -> Dict[str, Any]:
        """
        Main entry point for processing citizen chat queries as a Case Worker.
        """
        clean_msg = message.strip()
        lang = detect_language(clean_msg)

        # Step 6: Casual Conversation / Greeting Routing to Sarvam AI
        if self._is_casual_query(clean_msg):
            return self._handle_casual_query(clean_msg, lang)

        # Update Conversation Memory with any extracted profile parameters
        memory = self._update_conversation_memory(session_id, clean_msg)
        logger.info(f"[AI Case Worker Memory] Session '{session_id}' ({lang}) state: {memory}")

        # Step 1: Check if crucial profile information is missing for detected citizen category
        category = memory.get("category") or self._detect_category_from_text(clean_msg)
        missing_question = self._check_missing_profile_questions(clean_msg, memory, category, lang)

        if missing_question:
            # Interactive Step 1: Ask only missing profile questions first in user's language
            return {
                "reply": missing_question,
                "matched_schemes": [],
                "missing_fields": self._get_missing_fields_list(memory, category),
                "can_create_reminder": False
            }

        # Step 2: Search SQLite for Top 5 matching schemes using updated memory
        retrieved_schemes = search_service.search_schemes(clean_msg, db, limit=5, citizen_context=memory)
        logger.info(f"[AI Search] Retrieved {len(retrieved_schemes)} schemes for query: '{clean_msg}'")

        # Step 3: Multilingual Gemini RAG Case Worker Explanation
        rag_response = gemini_rag_service.generate_grounded_response(
            user_query=clean_msg,
            retrieved_schemes=retrieved_schemes,
            citizen_context=memory,
            language=lang
        )

        matched_schemes = []
        for s in retrieved_schemes:
            slug = (s.slug or "").strip()
            official_link = f"https://www.myscheme.gov.in/schemes/{slug}" if slug else ""
            cat = s.schemeCategory or s.category_legacy or "Welfare Scheme"
            
            matched_schemes.append({
                "id": s.id,
                "title": s.scheme_name or s.title_legacy,
                "category": cat,
                "description": s.details or s.description_legacy or "",
                "benefits": s.benefits or "Financial / Services assistance provided.",
                "eligibility": s.eligibility or "Eligible Indian citizens.",
                "required_documents": s.documents or s.required_documents_legacy or "Standard Identity Proof",
                "application": s.application or "Visit official portal or local designated office.",
                "official_link": official_link,
                "deadline": s.deadline or "Open Year Round",
                "match_reason": f"Eligible for your profile under {cat}."
            })

        reply_text = rag_response.get("reply", "").replace("*", "")

        return {
            "reply": reply_text,
            "matched_schemes": matched_schemes,
            "missing_fields": [],
            "can_create_reminder": True
        }

    def _is_casual_query(self, message: str) -> bool:
        """Check if message is a greeting, casual chat, or non-scheme inquiry."""
        lower = message.strip().lower()

        # Domain words in English, Hinglish, and Hindi
        scheme_domain_words = {
            "scheme", "yojana", "scholarship", "loan", "farmer", "kisan",
            "pension", "hospital", "money", "grant", "subsidy", "apply",
            "eligibility", "benefit", "document", "job", "house", "school",
            "college", "passed", "income", "acre", "lakh", "crore", "udid",
            "bpl", "ration", "caste", "certificate", "fee", "guideline", "guidelines",
            "support", "help", "aid", "योजना", "छात्रवृत्ति", "किसान", "पेंशन",
            "अस्पताल", "ऋण", "लोन", "पात्रता", "लाभ", "दस्तावेज", "आवेदन"
        }

        if any(w in lower for w in scheme_domain_words):
            return False

        greetings = {
            "hi", "hello", "hey", "namaste", "good morning", "good evening",
            "good afternoon", "thank you", "thanks", "who are you", "what is your name",
            "kaise ho", "kaise hain", "bye", "goodbye", "how are you", "नमस्ते", "प्रणाम", "धन्यवाद"
        }

        if lower in greetings:
            return True

        words = lower.split()
        if len(words) <= 3 and not any(w in lower for w in scheme_domain_words):
            return True

        return False

    def _handle_casual_query(self, message: str, lang: str) -> Dict[str, Any]:
        """Route general/casual conversation to Sarvam AI with target language instruction."""
        if sarvam_client.is_configured():
            lang_prompt = "Respond in Hindi." if lang == "hi" else "Respond in Hinglish." if lang == "hinglish" else "Respond in English."
            messages = [
                {
                    "role": "system",
                    "content": f"You are JanSathi AI, an empathetic AI Government Case Worker in India. {lang_prompt} Respond politely, concisely, and warmly."
                },
                {"role": "user", "content": message}
            ]
            reply = sarvam_client.completion(messages, temperature=0.3)
            if reply:
                return {
                    "reply": reply.replace("*", ""),
                    "matched_schemes": [],
                    "missing_fields": [],
                    "can_create_reminder": False
                }

        # Multilingual fallback greetings
        if lang == "hi":
            fallback = "नमस्ते! मैं जनसाथी AI हूँ, आपका समर्पित केस वर्कर। आज मैं आपकी क्या सहायता कर सकता हूँ? आप छात्रवृत्ति, किसान योजना, पेंशन, स्वास्थ्य कार्ड या बिजनेस लोन के बारे में पूछ सकते हैं।"
        elif lang == "hinglish":
            fallback = "Namaste! Main JanSathi AI hun, aapka dedicated AI Government Case Worker. Aaj main aapki kya madad kar sakta hun? Aap scholarship, kisan yojana, pension, ya mudra loan ke baare me pooch sakte hain."
        else:
            fallback = "Namaste! I am JanSathi AI, your dedicated AI Government Case Worker. How can I assist you today? You can ask about student scholarships, farmer support, senior pensions, health cover, or business loans."

        return {
            "reply": fallback,
            "matched_schemes": [],
            "missing_fields": [],
            "can_create_reminder": False
        }

    def _detect_category_from_text(self, text: str) -> Optional[str]:
        lower = text.lower()
        if any(w in lower for w in ['scholarship', 'student', 'study', 'class 10', 'class 12', 'college', 'school', 'passed', 'छात्र', 'छात्रवृत्ति', 'पढ़ाई']):
            return "Scholarships"
        if any(w in lower for w in ['farmer', 'kisan', 'crop', 'wheat', 'rice', 'acres', 'land', 'harvest', 'agriculture', 'किसान', 'फसल', 'खेती', 'ज़मीन']):
            return "Farmers"
        if any(w in lower for w in ['tailoring', 'shg', 'lakhpati', 'mother', 'pregnant', 'girl', 'woman', 'women', 'female', 'महिला', 'बेटी', 'नारी']):
            return "Women"
        if any(w in lower for w in ['senior', '70', '60', 'pension', 'elderly', 'old age', 'jeevan pramaan', 'पेंशन', 'बुजुर्ग', 'वृद्ध']):
            return "Senior Citizens"
        if any(w in lower for w in ['health', 'hospital', 'treatment', 'medical', 'ayushman', 'disease', 'स्वास्थ्य', 'अस्पताल', 'इलाज']):
            return "Health"
        if any(w in lower for w in ['house', 'housing', 'build a house', 'pmay', 'home', 'awas', 'मकान', 'घर', 'आवास']):
            return "Housing"
        if any(w in lower for w in ['unemployed', 'job', 'skill', 'mgnrega', 'training', 'employment', 'artisan', 'रोजगार', 'नौकरी', 'कौशल']):
            return "Employment"
        if any(w in lower for w in ['shop', 'business', 'mudra', 'loan', 'enterprise', 'store', 'व्यापार', 'दुकान', 'लोन']):
            return "Business"
        if any(w in lower for w in ['disability', 'disabled', 'divyang', 'handicap', 'wheelchair', 'udid', 'दिव्यांग', 'विकलांग']):
            return "Disability"
        return None

    def _check_missing_profile_questions(self, message: str, memory: Dict[str, Any], category: Optional[str], lang: str) -> Optional[str]:
        """
        Step 1: Check if essential profile details are missing for the specific citizen category.
        Returns targeted questions in Hindi, Hinglish, or English.
        """
        lower = message.lower()
        words = lower.split()

        # Rich query check
        if len(words) >= 9 and any(w in lower for w in ['passed', 'percent', '%', 'acre', 'acres', 'lakh', 'income', 'rs', '₹', 'साल', 'आय', 'एकड़']):
            return None

        # 🎓 Student Profile Check
        if category == "Scholarships":
            missing = []
            if not memory.get("state"):
                missing.append("Which state are you from?" if lang == "en" else "Aap kis state se hain?" if lang == "hinglish" else "आप किस राज्य से हैं?")
            if not memory.get("education"):
                missing.append("What is your highest qualification? (Class 10, Class 12, Graduation)" if lang == "en" else "Aapki highest qualification kya hai? (10th, 12th, Graduation)" if lang == "hinglish" else "आपकी उच्चतम योग्यता क्या है? (कक्षा 10, कक्षा 12, ग्रेजुएशन आदि)")
            if not memory.get("annual_income"):
                missing.append("What is your annual family income?" if lang == "en" else "Aapki annual family income kitni hai?" if lang == "hinglish" else "आपके परिवार की वार्षिक आय कितनी है?")

            if len(missing) >= 2:
                if lang == "hi":
                    header = "नमस्ते! आपके AI सरकारी केस वर्कर के रूप में, मैं आपको सर्वश्रेष्ठ छात्रवृत्ति और शिक्षा योजनाओं की जानकारी दूंगा।\n\nआपकी सही योजना चुनने के लिए कृपया बताएं:\n"
                    footer = "\n\nयह जानकारी साझा करते ही मैं आपको चरण-दर-चरण मार्गदर्शन दूंगा!"
                elif lang == "hinglish":
                    header = "Namaste! Aapke AI Government Case Worker ke roop me, main aapko best scholarships aur education schemes dhundhne me madad karunga.\n\nAapke liye sahi yojana match karne ke liye kripya batayein:\n"
                    footer = "\n\nJante hi main aapko step-by-step guide karunga!"
                else:
                    header = "Namaste! As your AI Government Case Worker, I would be happy to guide you to the best student scholarships and education schemes.\n\nTo recommend the exact schemes you qualify for, please share a few quick details:\n"
                    footer = "\n\nOnce you share these, I will guide you step-by-step!"

                return header + "\n".join([f"• {q}" for q in missing]) + footer

        # 👨‍🌾 Farmer Profile Check
        elif category == "Farmers":
            missing = []
            if not memory.get("state"):
                missing.append("Which state are you from?" if lang == "en" else "Aap kis state se hain?" if lang == "hinglish" else "आप किस राज्य से हैं?")
            if not memory.get("land"):
                missing.append("How much land do you own? (in acres)" if lang == "en" else "Aapke paas kitni zameen hai? (acres me)" if lang == "hinglish" else "आपके पास कितनी एकड़ ज़मीन है?")
            if not memory.get("crop"):
                missing.append("Which crop do you cultivate?" if lang == "en" else "Aap konsi crop cultivate karte hain?" if lang == "hinglish" else "आप कौन सी फसल उगाते हैं?")

            if len(missing) >= 2:
                if lang == "hi":
                    header = "नमस्ते! मैं आपको कृषि सहायता और फसल सुरक्षा योजनाओं की पूरी जानकारी दूंगा।\n\nकृपया बताएं:\n"
                    footer = "\n\nजानकारी साझा करते ही मैं आपकी खेती के लिए सटीक योजनाएं मैच करूंगा!"
                elif lang == "hinglish":
                    header = "Namaste! Main aapko kheti aur crop support schemes ki poori jankari dunga.\n\nKripya batayein:\n"
                    footer = "\n\nYe details batate hi main aapke farm ke liye exact schemes match karunga!"
                else:
                    header = "Namaste! As your AI Government Case Worker, I am here to help you get the right government support for your farming.\n\nTo find the exact crop insurance, income support, or subsidies for you, please tell me:\n"
                    footer = "\n\nSharing these will help me match the exact schemes for your farm!"

                return header + "\n".join([f"• {q}" for q in missing]) + footer

        # 👩 Women Welfare Check
        elif category == "Women":
            if not memory.get("women_support_type"):
                if lang == "hi":
                    return "नमस्ते! आपके AI सरकारी केस वर्कर के रूप में, मैं महिला कल्याण योजनाओं में आपकी सहायता करने के लिए तैयार हूँ।\n\nकृपया बताएं:\n• क्या आप शिक्षा, रोजगार, या व्यवसाय सहायता की तलाश में हैं?"
                elif lang == "hinglish":
                    return "Namaste! Aapke AI Government Case Worker ke roop me, main mahila kalyan yojanao me aapki madad karne ke liye tayar hun.\n\nKripya batayein:\n• Kya aap education, employment, ya business support ki talash me hain?"
                else:
                    return "Namaste! As your AI Government Case Worker, I am happy to assist you with women welfare and empowerment schemes.\n\nCould you please tell me:\n• Are you looking for education, employment, or business support?"

        # 👴 Senior Citizen Check
        elif category == "Senior Citizens":
            missing = []
            if not memory.get("age"):
                missing.append("Your age?" if lang == "en" else "Aapki umar (age) kya hai?" if lang == "hinglish" else "आपकी उम्र कितनी है?")
            if not memory.get("bpl_card"):
                missing.append("Do you have a BPL card?" if lang == "en" else "Kya aapke paas BPL card hai?" if lang == "hinglish" else "क्या आपके पास बीपीएल (BPL) कार्ड है?")

            if len(missing) >= 1:
                if lang == "hi":
                    header = "नमस्ते! आपके AI सरकारी केस वर्कर के रूप में, मैं आपको बुजुर्ग पेंशन और स्वास्थ्य सुरक्षा योजनाओं की जानकारी दूंगा।\n\nकृपया बताएं:\n"
                elif lang == "hinglish":
                    header = "Namaste! Aapke AI Government Case Worker ke roop me, main senior citizen pension aur health cover ki jankari dunga.\n\nKripya batayein:\n"
                else:
                    header = "Namaste! As your AI Government Case Worker, I can guide you to senior citizen pensions and healthcare coverage.\n\nPlease share:\n"

                return header + "\n".join([f"• {q}" for q in missing])

        return None

    def _get_missing_fields_list(self, memory: Dict[str, Any], category: Optional[str]) -> List[str]:
        missing = []
        if not memory.get("state"):
            missing.append("state")
        if not memory.get("annual_income"):
            missing.append("income")
        if not memory.get("education"):
            missing.append("qualification")
        return missing

    def _update_conversation_memory(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Maintain backend conversation memory across turns.
        Stores State, Age, Education, Income, Occupation, Gender, Land, Crop, BPL Card.
        """
        if session_id not in CONVERSATION_MEMORY:
            CONVERSATION_MEMORY[session_id] = {}

        memory = CONVERSATION_MEMORY[session_id]
        lower = message.lower()

        # Extract State
        states = [
            'uttar pradesh', 'up', 'punjab', 'bihar', 'maharashtra', 'rajasthan', 'mp',
            'madhya pradesh', 'delhi', 'kerala', 'gujarat', 'puducherry', 'karnataka',
            'west bengal', 'chhattisgarh', 'andhra pradesh', 'tamil nadu', 'haryana', 'odisha', 'tripura',
            'उत्तर प्रदेश', 'पंजाब', 'बिहार', 'राजस्थान', 'मध्य प्रदेश', 'दिल्ली'
        ]
        for st in states:
            if st in lower:
                memory["state"] = st.title()
                break

        # Extract Education
        if any(w in lower for w in ["12th", "class 12", "class xii", "intermediate", "higher secondary", "12वीं", "12वी"]):
            memory["education"] = "Class 12th / Intermediate"
        elif any(w in lower for w in ["10th", "class 10", "class x", "matric", "sslc", "10वीं", "10वी"]):
            memory["education"] = "Class 10th / Matric"
        elif any(w in lower for w in ["diploma", "polytechnic", "डिप्लोमा"]):
            memory["education"] = "Diploma"
        elif any(w in lower for w in ["graduate", "degree", "btech", "ba", "bsc", "bcom", "college", "ग्रेजुएशन"]):
            memory["education"] = "Graduation"

        # Extract Annual Income
        income_match = re.search(r'(\d+(\.\d+)?)\s*(lakh|lac|k|thousand|lakhs|लाख|हजार)', lower)
        if income_match:
            val = float(income_match.group(1))
            unit = income_match.group(3)
            if 'lakh' in unit or 'lac' in unit or 'लाख' in unit:
                memory["annual_income"] = f"₹{val} Lakh"
            elif 'k' in unit or 'thousand' in unit or 'हजार' in unit:
                memory["annual_income"] = f"₹{val} Thousand"
        elif 'bpl' in lower or 'below poverty line' in lower or 'गरीबी रेखा' in lower:
            memory["annual_income"] = "BPL"
            memory["bpl_card"] = "Yes"

        if 'bpl' in lower or 'बीपीएल' in lower:
            memory["bpl_card"] = "Yes"

        # Extract Age
        age_match = re.search(r'(\b\d{1,2}\b)\s*(years|yr|yrs|year old|yr old|age|साल|वर्ष)', lower)
        if age_match:
            memory["age"] = int(age_match.group(1))

        # Extract Gender
        if any(w in lower for w in ["female", "woman", "women", "girl", "महिला", "लड़की"]):
            memory["gender"] = "Female"
        elif any(w in lower for w in ["male", "man", "boy", "पुरुष", "लड़का"]):
            memory["gender"] = "Male"

        # Extract Land & Crop for Farmers
        land_match = re.search(r'(\d+(\.\d+)?)\s*(acre|acres|bigha|hectare|एकड़|बीघा)', lower)
        if land_match:
            memory["land"] = f"{land_match.group(1)} {land_match.group(3)}"
        for crop_name in ['wheat', 'rice', 'paddy', 'cotton', 'sugarcane', 'mustard', 'pulses', 'maize', 'गेहूं', 'धान', 'चावल', 'कपास']:
            if crop_name in lower:
                memory["crop"] = crop_name.title()
                break

        # Extract Occupation & Category
        if any(w in lower for w in ["farmer", "kisan", "crop", "agriculture", "land", "किसान", "खेती", "फसल"]):
            memory["occupation"] = "Farmer"
            memory["category"] = "Farmers"
        elif any(w in lower for w in ["student", "study", "scholarship", "passed", "छात्र", "छात्रवृत्ति", "पढ़ाई"]):
            memory["occupation"] = "Student"
            memory["category"] = "Scholarships"
        elif any(w in lower for w in ["business", "shop", "msme", "store", "startup", "व्यापार", "दुकान"]):
            memory["occupation"] = "Business Owner"
            memory["category"] = "Business"

        CONVERSATION_MEMORY[session_id] = memory
        return memory


# Singleton instance
ai_case_worker = AICaseWorkerService()

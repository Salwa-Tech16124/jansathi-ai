import json
import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.services.sarvam_service import sarvam_client

logger = logging.getLogger("jansathi.ai_service")

# 10 Citizen Group Categories
CATEGORIES = [
    "Scholarships",
    "Farmers",
    "Women",
    "Senior Citizens",
    "Health",
    "Housing",
    "Employment",
    "Business",
    "Disability",
    "Child Welfare"
]


class AICaseWorkerService:
    """
    Unified AI Case Worker Service supporting 10 Citizen Groups.
    
    Uses Sarvam AI as the primary reasoning engine when SARVAM_API_KEY is configured.
    Falls back gracefully to deterministic rule-based analysis across all 10 categories.
    """

    def analyze_and_respond(self, message: str, db: Session) -> Dict[str, Any]:
        """
        Analyze citizen query and generate category-focused scheme matches & targeted follow-up questions.
        """
        db_schemes = db.query(Scheme).all()

        # Try Sarvam AI Reasoning first
        if sarvam_client.is_configured():
            sarvam_result = self._analyze_with_sarvam(message, db_schemes)
            if sarvam_result:
                return sarvam_result
            logger.info("[AI Case Worker] Sarvam AI returned empty/failed. Using rule engine fallback.")

        # Fallback to local rule engine
        return self._analyze_with_rule_engine(message, db_schemes)

    def _analyze_with_sarvam(self, message: str, db_schemes: List[Scheme]) -> Optional[Dict[str, Any]]:
        schemes_context = [
            {
                "id": s.id,
                "title": s.title,
                "category": s.category,
                "description": s.description,
                "eligibility": s.eligibility,
                "required_documents": s.required_documents,
                "deadline": s.deadline or "Open Year Round"
            }
            for s in db_schemes
        ]

        system_prompt = (
            "You are JanSathi AI, an empathetic Public Service Case Worker assisting Indian citizens across 10 groups:\n"
            "Scholarships, Farmers, Women, Senior Citizens, Health, Housing, Employment, Business, Disability, Child Welfare.\n\n"
            "CRITICAL RULES:\n"
            "1. DATABASE_SCHEMES is the ONLY source of truth. DO NOT invent or mention external schemes.\n"
            "2. First identify which citizen category the user belongs to.\n"
            "3. Recommend schemes PRIMARILY matching that category.\n"
            "4. If crucial info (state, age, income, class, land, business type) is missing, include ONE simple category-specific follow-up question in your reply.\n"
            "5. Output strictly in valid JSON format with keys:\n"
            "{\n"
            '  "reply": "Conversational response in Hindi/Hinglish/English",\n'
            '  "matched_scheme_ids": [integer IDs of matched schemes],\n'
            '  "scheme_match_reasons": {"<scheme_id>": "Brief eligibility reason"},\n'
            '  "missing_fields": ["state", "income", etc.],\n'
            '  "can_create_reminder": true\n'
            "}\n"
        )

        user_content = (
            f"CITIZEN MESSAGE: \"{message}\"\n\n"
            f"DATABASE_SCHEMES:\n{json.dumps(schemes_context, ensure_ascii=False)}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        raw_completion = sarvam_client.completion(messages, temperature=0.1)
        if not raw_completion:
            return None

        try:
            cleaned_json = raw_completion.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            cleaned_json = cleaned_json.strip()

            parsed = json.loads(cleaned_json)

            matched_scheme_ids = parsed.get("matched_scheme_ids", [])
            match_reasons = parsed.get("scheme_match_reasons", {})
            db_scheme_dict = {s.id: s for s in db_schemes}

            matched_schemes = []
            for sid in matched_scheme_ids:
                if sid in db_scheme_dict:
                    s = db_scheme_dict[sid]
                    reason = match_reasons.get(str(sid)) or match_reasons.get(sid) or f"Eligible under {s.category} category."
                    matched_schemes.append({
                        "id": s.id,
                        "title": s.title,
                        "category": s.category,
                        "description": s.description,
                        "eligibility": s.eligibility,
                        "required_documents": s.required_documents,
                        "deadline": s.deadline or "Open Year Round",
                        "match_reason": reason
                    })

            return {
                "reply": parsed.get("reply", "Namaste! Here are the public schemes matched to your profile."),
                "matched_schemes": matched_schemes,
                "missing_fields": parsed.get("missing_fields", []),
                "can_create_reminder": bool(parsed.get("can_create_reminder", True))
            }

        except Exception as err:
            logger.error(f"[AI Case Worker] JSON Parse error: {err}")
            return None

    def _analyze_with_rule_engine(self, message: str, db_schemes: List[Scheme]) -> Dict[str, Any]:
        lower = message.lower()
        category = self._detect_citizen_category(lower)
        entities = self._extract_entities_local(lower)

        matched_schemes: List[Dict[str, Any]] = []
        missing_fields: List[str] = []

        # Filter schemes primarily by detected category
        for s in db_schemes:
            match_score = 0
            reasons = []

            if category and s.category.lower() == category.lower():
                match_score += 4
                reasons.append(f"Direct match for {s.category} welfare category.")
            
            # Secondary entity boosts
            if entities["age"] and entities["age"] >= 60 and s.category == "Senior Citizens":
                match_score += 3
                reasons.append(f"Eligible for senior citizens aged 60+ (your age: {entities['age']}).")

            if entities["gender"] == "Female" and s.category in ["Women", "Business", "Scholarships"]:
                match_score += 1
                reasons.append("Includes special provisions for women & girl students.")

            if match_score > 0:
                matched_schemes.append({
                    "id": s.id,
                    "title": s.title,
                    "category": s.category,
                    "description": s.description,
                    "eligibility": s.eligibility,
                    "required_documents": s.required_documents,
                    "deadline": s.deadline or "Open Year Round",
                    "match_reason": " ".join(reasons) if reasons else "Matches your category query."
                })

        # Category-Specific Follow-Up Questions
        followup_questions = {
            "Scholarships": "Aap kis class/degree me padh rahe hain, aur aapka annual family income kitna hai?",
            "Farmers": "Aapke paas kitni acre kheti zameen hai aur aap kis state se hain?",
            "Women": "Kya aap Self-Help Group (SHG) se judi hain ya apna kaam shuru karna chahti hain?",
            "Senior Citizens": "Aapki umar kitni hai aur kya aap BPL category me aate hain?",
            "Health": "Kya aapke paas Ayushman Bharat card ya Ration Card hai?",
            "Housing": "Kya aap rural (gramin) ya urban kshetra se hain aur aapka budget kitna hai?",
            "Employment": "Aapki qualification kya hai aur aap kis skill training me ruchi rakhte hain?",
            "Business": "Aap kis prakar ka business/dukaan kholna chahte hain aur kitna loan required hai?",
            "Disability": "Kya aapke paas UDID Disability Certificate hai aur kitna percentage disability hai?",
            "Child Welfare": "Bachhe ki umar kitni hai aur kya guardian documents uplabdh hain?"
        }

        if not entities["state"]:
            missing_fields.append("state")

        if category:
            followup = followup_questions.get(category, "Kripya apne state aur income ke bare me batayein.")
        else:
            followup = "Kripya batayein: Kya aap Student, Farmer, Senior Citizen, Woman, Health, ya Business scheme chahte hain?"

        if matched_schemes:
            titles = [f"**{m['title']}**" for m in matched_schemes[:3]]
            reply = (
                f"Namaste! Aapke request ({category or 'Citizen Service'}) ke aadhar par **{len(matched_schemes)} scheme(s)** payi gayi hain: "
                f"{', '.join(titles)}.\n\n"
                f"📌 *Quick Question:* {followup}\n\n"
                f"Niche diye gaye scheme cards par 'Set Reminder' button se aap application deadline set kar sakte hain."
            )
        else:
            missing_fields = ["category", "details"]
            reply = f"Namaste! {followup}"

        return {
            "reply": reply,
            "matched_schemes": matched_schemes[:4],
            "missing_fields": missing_fields,
            "can_create_reminder": True
        }

    def _detect_citizen_category(self, lower: str) -> Optional[str]:
        """Detect which of the 10 citizen categories the query belongs to."""
        if any(w in lower for w in ['scholarship', 'student', 'study', 'class 10', 'class 12', 'college', 'school', 'pass']):
            return "Scholarships"
        if any(w in lower for w in ['farmer', 'kisan', 'crop', 'wheat', 'rice', 'acres', 'land', 'harvest', 'agriculture']):
            return "Farmers"
        if any(w in lower for w in ['tailoring', 'shg', 'lakhpati', 'mother', 'pregnant', 'girl child', 'woman', 'women', 'female']):
            return "Women"
        if any(w in lower for w in ['senior', '70', '60', 'pension', 'elderly', 'old age', 'jeevan pramaan']):
            return "Senior Citizens"
        if any(w in lower for w in ['health', 'hospital', 'treatment', 'medical', 'ayushman', 'disease', 'doctor']):
            return "Health"
        if any(w in lower for w in ['house', 'housing', 'build a house', 'pmay', 'home', 'roof', 'shelter']):
            return "Housing"
        if any(w in lower for w in ['unemployed', 'job', 'skill', 'mgnrega', 'training', 'vishwakarma', 'artisan', 'employment']):
            return "Employment"
        if any(w in lower for w in ['shop', 'business', 'mudra', 'loan', 'enterprise', 'grocery', 'store']):
            return "Business"
        if any(w in lower for w in ['disability', 'disabled', 'divyang', 'handicap', 'wheelchair', 'udid']):
            return "Disability"
        if any(w in lower for w in ['child', 'orphan', 'anganwadi', 'poshan', 'vatsalya', 'kids']):
            return "Child Welfare"
        return None

    def _extract_entities_local(self, lower: str) -> Dict[str, Any]:
        entities: Dict[str, Any] = {
            "age": None, "gender": None, "state": None, "income": None
        }

        age_match = re.search(r'(\b\d{1,2}\b)\s*(years|yr|yrs|year old|yr old|age)', lower)
        if age_match:
            entities["age"] = int(age_match.group(1))

        if any(w in lower for w in ['female', 'woman', 'women', 'girl']):
            entities["gender"] = "Female"

        for st in ['uttar pradesh', 'up', 'punjab', 'bihar', 'maharashtra', 'rajasthan', 'mp', 'delhi', 'kerala', 'gujarat']:
            if st in lower:
                entities["state"] = st.title()
                break

        return entities


# Singleton instance
ai_case_worker = AICaseWorkerService()

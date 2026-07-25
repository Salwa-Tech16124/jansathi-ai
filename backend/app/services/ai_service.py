import json
import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.services.sarvam_service import sarvam_client

logger = logging.getLogger("jansathi.ai_service")


class AICaseWorkerService:
    """
    Unified AI Case Worker Service for JanSathi AI.
    
    Uses Sarvam AI as the primary reasoning engine when SARVAM_API_KEY is configured and valid.
    Falls back gracefully to deterministic rule-based analysis if Sarvam AI is unconfigured or encounters an error.
    """

    def analyze_and_respond(self, message: str, db: Session) -> Dict[str, Any]:
        """
        Analyze citizen query and generate scheme matches, follow-up questions, and response.
        """
        # Fetch active government schemes from SQLite database (Source of Truth)
        db_schemes = db.query(Scheme).all()

        # Try Sarvam AI Reasoning first if configured
        if sarvam_client.is_configured():
            sarvam_result = self._analyze_with_sarvam(message, db_schemes)
            if sarvam_result:
                return sarvam_result
            logger.info("[AI Case Worker] Sarvam AI call returned None or failed. Falling back to local rule engine.")

        # Fallback to local rule-based AI engine
        return self._analyze_with_rule_engine(message, db_schemes)

    def _analyze_with_sarvam(self, message: str, db_schemes: List[Scheme]) -> Optional[Dict[str, Any]]:
        """
        Use Sarvam AI to reason over user message and database schemes.
        Strictly prevents hallucination of non-existent schemes.
        """
        # Format database schemes as JSON grounding context
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
            "You are JanSathi AI, an empathetic and official Public Service Case Worker assisting Indian citizens in Hindi, Hinglish, or English.\n"
            "CRITICAL RULES:\n"
            "1. The provided DATABASE_SCHEMES list is the ONLY source of truth. DO NOT invent or fabricate any external government scheme.\n"
            "2. Analyze the citizen message to extract entities (age, occupation, gender, state, district, income, need).\n"
            "3. If crucial details are missing for matching specific schemes, ask ONE simple, polite follow-up question instead of guessing.\n"
            "4. Match only schemes from DATABASE_SCHEMES that fit the citizen's profile.\n"
            "5. Respond ONLY in valid JSON format with the following keys:\n"
            "{\n"
            '  "reply": "Conversational reply in Hindi/Hinglish/English",\n'
            '  "matched_scheme_ids": [integer IDs of matched database schemes],\n'
            '  "scheme_match_reasons": {"<scheme_id>": "Brief reason why this scheme matches"},\n'
            '  "missing_fields": ["state", "age", etc.],\n'
            '  "can_create_reminder": true\n'
            "}\n"
            "No extra markdown surrounding text outside the JSON."
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
            # Clean possible markdown block markers
            cleaned_json = raw_completion.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            cleaned_json = cleaned_json.strip()

            parsed = json.loads(cleaned_json)

            # Map matched_scheme_ids back to full database objects
            matched_scheme_ids = parsed.get("matched_scheme_ids", [])
            match_reasons = parsed.get("scheme_match_reasons", {})
            db_scheme_dict = {s.id: s for s in db_schemes}

            matched_schemes = []
            for sid in matched_scheme_ids:
                if sid in db_scheme_dict:
                    s = db_scheme_dict[sid]
                    reason = match_reasons.get(str(sid)) or match_reasons.get(sid) or f"Matches your query for {s.category} assistance."
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
                "reply": parsed.get("reply", "Namaste! I am here to help you access citizen welfare services."),
                "matched_schemes": matched_schemes,
                "missing_fields": parsed.get("missing_fields", []),
                "can_create_reminder": bool(parsed.get("can_create_reminder", True))
            }

        except Exception as err:
            logger.error(f"[AI Case Worker] Error parsing Sarvam AI JSON completion: {err}")
            return None

    def _analyze_with_rule_engine(self, message: str, db_schemes: List[Scheme]) -> Dict[str, Any]:
        """
        Deterministic Rule-based Fallback AI Engine.
        """
        lower = message.lower()
        entities = self._extract_entities_local(lower)
        matched_schemes: List[Dict[str, Any]] = []
        missing_fields: List[str] = []

        words = message.strip().split()
        if len(words) < 4 and not entities["need"] and not entities["occupation"]:
            missing_fields = ["occupation", "age", "state", "need"]
            return {
                "reply": "Namaste! App konse state se hain aur kis vishay (Kisan, Pension, Scholarship, Health, ya Women welfare) me sahayata chahte hain?",
                "matched_schemes": [],
                "missing_fields": missing_fields,
                "can_create_reminder": False
            }

        target_category = entities["need"]

        for s in db_schemes:
            match_score = 0
            reasons = []

            if target_category and s.category.lower() == target_category.lower():
                match_score += 3
                reasons.append(f"Matches your request for {s.category} public services.")
            elif not target_category:
                if entities["occupation"] and entities["occupation"].lower() in s.category.lower():
                    match_score += 2
                    reasons.append(f"Designed for {entities['occupation']}s.")

            if entities["age"] and entities["age"] >= 60 and s.category == "Senior Citizens":
                match_score += 2
                reasons.append(f"Eligible for senior citizens aged 60+ (your age: {entities['age']}).")

            if entities["gender"] == "Female" and s.category == "Women":
                match_score += 2
                reasons.append("Empowerment scheme for women and mothers.")

            if entities["occupation"] == "Student" and s.category == "Scholarships":
                match_score += 2
                reasons.append("Provides educational scholarship assistance.")

            if match_score > 0:
                matched_schemes.append({
                    "id": s.id,
                    "title": s.title,
                    "category": s.category,
                    "description": s.description,
                    "eligibility": s.eligibility,
                    "required_documents": s.required_documents,
                    "deadline": s.deadline or "Open Year Round",
                    "match_reason": " ".join(reasons) if reasons else "Relevant government welfare scheme."
                })

        if not entities["state"]:
            missing_fields.append("state")
        if not entities["income"]:
            missing_fields.append("income")

        if matched_schemes:
            titles = [f"**{m['title']}**" for m in matched_schemes[:3]]
            reply = (
                f"Namaste! Aapke profile ke aadhar par **{len(matched_schemes)} government scheme(s)** milne ki sambhavna hai: "
                f"{', '.join(titles)}.\n\n"
                f"Niche diye gaye cards me eligibility aur required documents dekhein. "
                f"Aap seedhe yahan se reminder bhi set kar sakte hain!"
            )
        else:
            missing_fields = ["occupation", "need"]
            reply = (
                "Kripya thoda vistar se batayein: Kya aap Kisan, Student, Senior Citizen, ya Health Cover ke bare me jankari chahte hain?"
            )

        return {
            "reply": reply,
            "matched_schemes": matched_schemes[:4],
            "missing_fields": missing_fields,
            "can_create_reminder": True
        }

    def _extract_entities_local(self, lower: str) -> Dict[str, Any]:
        """Local entity extractor helper."""
        entities: Dict[str, Any] = {
            "age": None, "occupation": None, "gender": None, 
            "state": None, "district": None, "income": None, "need": None
        }

        age_match = re.search(r'(\b\d{1,2}\b)\s*(years|yr|yrs|year old|yr old|age)', lower)
        if age_match:
            entities["age"] = int(age_match.group(1))
        elif any(w in lower for w in ['senior', 'old age', 'elderly', 'pension']):
            entities["age"] = 65

        if any(w in lower for w in ['farmer', 'kisan', 'agriculture', 'crop']):
            entities["occupation"] = "Farmer"
        elif any(w in lower for w in ['student', 'school', 'class', 'college']):
            entities["occupation"] = "Student"
        elif any(w in lower for w in ['housewife', 'shg', 'woman', 'mother', 'pregnant']):
            entities["occupation"] = "Self-Help Group / Women"

        if any(w in lower for w in ['female', 'woman', 'women', 'mother', 'girl']):
            entities["gender"] = "Female"

        if any(w in lower for w in ['scholarship', 'study', 'education']):
            entities["need"] = "Scholarships"
        elif any(w in lower for w in ['kisan', 'farmer', 'crop', 'agriculture']):
            entities["need"] = "Farmers"
        elif any(w in lower for w in ['woman', 'mother', 'pregnancy', 'shg']):
            entities["need"] = "Women"
        elif any(w in lower for w in ['pension', 'old age', 'senior', 'elderly']):
            entities["need"] = "Senior Citizens"
        elif any(w in lower for w in ['health', 'hospital', 'ayushman', 'medical']):
            entities["need"] = "Health"

        for st in ['uttar pradesh', 'up', 'bihar', 'maharashtra', 'rajasthan', 'mp', 'delhi']:
            if st in lower:
                entities["state"] = st.title()
                break

        return entities


# Singleton instance
ai_case_worker = AICaseWorkerService()

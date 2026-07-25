import re
import logging
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.scheme import Scheme

logger = logging.getLogger("jansathi.search_service")

# Synonym expansion map for query normalization
SYNONYM_GROUPS: List[Dict[str, Any]] = [
    {
        "category": "Education",
        "keywords": ["12", "12th", "class 12", "class xii", "intermediate", "higher secondary", "hsc", "plus two", "scholarship", "student", "school", "college"],
        "expansions": ["scholarship", "student", "education", "12th", "intermediate", "school", "college", "merit"]
    },
    {
        "category": "Education_10th",
        "keywords": ["10", "10th", "class 10", "class x", "metric", "sslc", "high school"],
        "expansions": ["scholarship", "student", "education", "10th", "matric", "school"]
    },
    {
        "category": "Agriculture",
        "keywords": ["farmer", "farmers", "kisan", "agriculture", "crop", "farming", "cultivator", "harvest", "wheat", "rice", "land", "soil"],
        "expansions": ["kisan", "farmer", "agriculture", "crop", "farming", "cultivator", "land"]
    },
    {
        "category": "Women",
        "keywords": ["women", "woman", "female", "mahila", "girl", "girls", "mother", "shg", "lakhpati", "nari"],
        "expansions": ["women", "mahila", "female", "girl", "mother", "shg"]
    },
    {
        "category": "Business",
        "keywords": ["business", "msme", "startup", "shop", "entrepreneur", "enterprise", "loan", "store", "merchant", "mudra", "capital"],
        "expansions": ["business", "msme", "enterprise", "entrepreneur", "loan", "shop"]
    },
    {
        "category": "Employment",
        "keywords": ["job", "employment", "work", "skill", "training", "unemployed", "artisan", "craftsman", "worker", "labor", "labour", "mgnrega"],
        "expansions": ["employment", "job", "skill", "training", "artisan", "worker"]
    },
    {
        "category": "Health",
        "keywords": ["hospital", "medical", "treatment", "health", "ayushman", "doctor", "medicine", "patient", "disease", "clinic"],
        "expansions": ["health", "medical", "treatment", "hospital", "ayushman", "medicine"]
    },
    {
        "category": "Housing",
        "keywords": ["house", "home", "pmay", "shelter", "building", "roof", "housing", "awas", "flat"],
        "expansions": ["housing", "house", "home", "awas", "pmay", "shelter"]
    },
    {
        "category": "Senior_Citizens",
        "keywords": ["senior", "elderly", "old age", "pension", "60", "70", "80", "jeevan pramaan"],
        "expansions": ["pension", "senior", "old age", "elderly"]
    },
    {
        "category": "Disability",
        "keywords": ["disability", "disabled", "divyang", "handicap", "wheelchair", "udid"],
        "expansions": ["disability", "disabled", "divyang", "handicap"]
    }
]


class IntelligentSearchService:
    """
    Intelligent SQLite Search Service for JanSathi AI.
    Searches across: scheme_name, details, benefits, eligibility, application, documents, tags.
    Normalizes query and applies synonym expansion across all citizen domains.
    """

    def normalize_query(self, query: str) -> List[str]:
        """
        Normalize query string and expand synonyms.
        """
        query_lower = query.lower()
        # Clean special chars except spaces & alphanumerics
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', query_lower)
        tokens = set(cleaned.split())

        expanded_terms: Set[str] = set(tokens)

        # Apply synonym expansions
        for group in SYNONYM_GROUPS:
            # Check if any keyword matches any token or phrase in query
            matches = False
            for kw in group["keywords"]:
                if kw in query_lower or kw in tokens:
                    matches = True
                    break
            if matches:
                for exp in group["expansions"]:
                    expanded_terms.add(exp)

        # Remove very short stop words unless numeric
        filtered_terms = [t for t in expanded_terms if len(t) > 1 or t.isdigit()]
        return filtered_terms

    def search_schemes(self, query: str, db: Session, limit: int = 5, citizen_context: Dict[str, Any] = None) -> List[Scheme]:
        """
        Perform intelligent SQLite retrieval returning Top 5 matching schemes.
        """
        terms = self.normalize_query(query)
        if not terms:
            terms = query.lower().split()

        # If citizen_context provides explicit state/occupation/category, add as search terms
        if citizen_context:
            if citizen_context.get("occupation"):
                terms.extend(citizen_context["occupation"].lower().split())
            if citizen_context.get("category"):
                terms.extend(citizen_context["category"].lower().split())
            if citizen_context.get("education"):
                terms.extend(citizen_context["education"].lower().split())

        # Deduplicate terms
        terms = list(dict.fromkeys(terms))

        # Construct SQLAlchemy OR filter across search fields
        conditions = []
        for term in terms[:10]: # Limit terms to top 10 for performance
            like_pat = f"%{term}%"
            conditions.append(Scheme.scheme_name.ilike(like_pat))
            conditions.append(Scheme.schemeCategory.ilike(like_pat))
            conditions.append(Scheme.tags.ilike(like_pat))
            conditions.append(Scheme.eligibility.ilike(like_pat))
            conditions.append(Scheme.benefits.ilike(like_pat))
            conditions.append(Scheme.details.ilike(like_pat))
            conditions.append(Scheme.documents.ilike(like_pat))

        # Query candidates from SQLite
        candidate_schemes = db.query(Scheme).filter(or_(*conditions)).limit(100).all()

        if not candidate_schemes:
            # Fallback to fetching first 20 schemes if query didn't hit indexed LIKEs
            candidate_schemes = db.query(Scheme).limit(50).all()

        # Rank candidates using TF-IDF style multi-field scoring
        scored_schemes = []
        for scheme in candidate_schemes:
            score = 0
            name_text = (scheme.scheme_name or scheme.title_legacy or "").lower()
            cat_text = (scheme.schemeCategory or scheme.category_legacy or "").lower()
            tags_text = (scheme.tags or "").lower()
            elig_text = (scheme.eligibility or "").lower()
            ben_text = (scheme.benefits or "").lower()
            det_text = (scheme.details or scheme.description_legacy or "").lower()
            doc_text = (scheme.documents or scheme.required_documents_legacy or "").lower()

            for term in terms:
                if term in name_text:
                    score += 10
                if term in tags_text:
                    score += 8
                if term in cat_text:
                    score += 7
                if term in elig_text:
                    score += 5
                if term in ben_text:
                    score += 4
                if term in det_text:
                    score += 3
                if term in doc_text:
                    score += 2

            # Boost if user's context attributes match
            if citizen_context:
                if citizen_context.get("gender") == "Female" and ("women" in cat_text or "girl" in tags_text or "mahila" in name_text):
                    score += 5
                if citizen_context.get("state") and citizen_context["state"].lower() in (scheme.level or "").lower():
                    score += 5

            if score > 0:
                scored_schemes.append((score, scheme))

        # Sort by score descending
        scored_schemes.sort(key=lambda x: x[0], reverse=True)

        results = [item[1] for item in scored_schemes[:limit]]

        # Fallback if less than limit results scored
        if len(results) < limit:
            existing_ids = {s.id for s in results}
            for candidate in candidate_schemes:
                if candidate.id not in existing_ids:
                    results.append(candidate)
                    if len(results) >= limit:
                        break

        return results[:limit]


# Singleton instance
search_service = IntelligentSearchService()

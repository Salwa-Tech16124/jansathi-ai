import datetime
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.scheme import Scheme

logger = logging.getLogger("jansathi.scheme_collector")

# Curated repository of newly released and upcoming 2026 relevant government schemes
LATEST_GOVT_SCHEMES: List[Dict[str, Any]] = [
    {
        "scheme_name": "PM Surya Ghar: Muft Bijli Yojana 2026",
        "slug": "pm-surya-ghar-muft-bijli-2026",
        "details": "Central Government scheme providing financial subsidy up to ₹78,000 for rooftop solar installation, delivering up to 300 units of free electricity per month for 1 Crore households across India.",
        "benefits": "Financial subsidy of ₹30,000 for 1kW system, ₹60,000 for 2kW, and ₹78,000 for 3kW or higher systems. Free electricity up to 300 units monthly and extra revenue from surplus power sell-back.",
        "eligibility": "Indian citizens owning a residential house with a suitable roof. Household annual income must be under ₹8 Lakh.",
        "application": "Apply online at National Portal for Rooftop Solar (pmsuryaghar.gov.in) with electricity consumer number and roof photos.",
        "documents": "Aadhaar Card, Electricity Bill, Bank Account Passbook, Property Ownership Proof / Roof Photo",
        "level": "Central",
        "schemeCategory": "Housing",
        "tags": "Solar, Free Electricity, Subsidy, Rooftop, Energy, Green Energy, PM Surya Ghar",
        "deadline": "Open Year Round"
    },
    {
        "scheme_name": "PM Vidyalaxmi Higher Education Loan Subvention Scheme 2026",
        "slug": "pm-vidyalaxmi-loan-subvention-2026",
        "details": "Collateral-free education loans up to ₹10 Lakh with 7.5% interest subvention for meritorious students pursuing higher education in top 860 Quality Higher Educational Institutions (QHEIs) in India.",
        "benefits": "100% collateral-free and guarantee-free education loan up to ₹10 Lakh. Full 7.5% interest subvention during the course moratorium period for families earning up to ₹8 Lakh per year.",
        "eligibility": "Meritorious students admitted to eligible top NIRF-ranked institutions in India for undergraduate/postgraduate degree courses.",
        "application": "Submit single unified application on PM Vidyalaxmi Portal (pmvidyalaxmi.gov.in).",
        "documents": "Admission Offer Letter, Class 10th & 12th Marksheets, Family Income Certificate, Aadhaar Card, Student Bank Account",
        "level": "Central",
        "schemeCategory": "Scholarships",
        "tags": "Education Loan, Subvention, College, Higher Studies, Student, Merit, Vidyalaxmi",
        "deadline": "2026-12-31"
    },
    {
        "scheme_name": "Digital Agriculture Mission: Kisan Drone Anudan Scheme 2026",
        "slug": "kisan-drone-anudan-scheme-2026",
        "details": "Government subsidy scheme offering 40% to 100% financial assistance for purchasing agricultural drones for precision spraying of fertilizers, bio-pesticides, and crop health monitoring.",
        "benefits": "100% grant (up to ₹10 Lakh) for ICAR institutes and KVKs; 50% grant (up to ₹5 Lakh) for SC/ST, small, marginal, and women farmers; 40% grant (up to ₹4 Lakh) for general farmers.",
        "eligibility": "Individual farmers, Farmer Producer Organizations (FPOs), Custom Hiring Centers (CHCs), and Agri-entrepreneurs.",
        "application": "Register on DBT Agriculture Portal or contact District Agriculture Officer / KVK Center.",
        "documents": "Aadhaar Card, Land Ownership Document (7/12 or Khatauni), FPO Registration Certificate, Bank Passbook, Drone Pilot Certificate",
        "level": "Central",
        "schemeCategory": "Farmers",
        "tags": "Drone, Farmer, Agriculture, Technology, Subsidy, FPO, Crop Spraying, Kisan Drone",
        "deadline": "Open Year Round"
    },
    {
        "scheme_name": "PM Vishwakarma Toolkit & Credit Assistance Scheme 2026",
        "slug": "pm-vishwakarma-artisan-scheme-2026",
        "details": "Comprehensive assistance scheme for traditional artisans and craftspeople covering 18 trades, providing e-vouchers worth ₹15,000 for advanced toolkits and collateral-free credit up to ₹3 Lakh at 5% interest.",
        "benefits": "₹15,000 e-voucher for modern toolkits, basic (5-7 days) & advanced (15 days) skill training with ₹500/day stipend, and ₹3 Lakh collateral-free loan (₹1 Lakh First Tranche + ₹2 Lakh Second Tranche).",
        "eligibility": "Artisans working with hands and tools in 18 traditional family trades (Carpenters, Blacksmiths, Goldsmiths, Potters, Tailors, Cobblers, Masons, Locksmiths, etc.). Minimum age 18 years.",
        "application": "Common Service Center (CSC) registration at pmvishwakarma.gov.in followed by 3-stage verification.",
        "documents": "Aadhaar Card, Mobile Number linked with Aadhaar, Bank Account Passbook, Skill Trade Certificate / Self-Declaration",
        "level": "Central",
        "schemeCategory": "Employment",
        "tags": "Vishwakarma, Artisan, Tailor, Carpenter, Toolkit, Loan, Skill Training, Employment",
        "deadline": "Open Year Round"
    },
    {
        "scheme_name": "Lakhpati Didi Micro-Enterprise Acceleration Scheme 2026",
        "slug": "lakhpati-didi-enterprise-2026",
        "details": "National mission empowering 3 Crore rural women associated with Self-Help Groups (SHGs) to establish micro-enterprises and achieve a sustained annual household income of at least ₹1 Lakh.",
        "benefits": "Interest subvention on micro-loans, free technical and marketing training, brand packaging support, and direct access to GEM Portal & e-Commerce platforms.",
        "eligibility": "Women members of recognized Self-Help Groups (SHGs) under DAY-NRLM in rural and semi-urban districts.",
        "application": "Apply through local Block Development Office (BDO) or Gram Panchayat SHG Cluster Coordinator.",
        "documents": "SHG Membership Passbook, Aadhaar Card, Individual Bank Passbook, Enterprise Business Plan",
        "level": "Central",
        "schemeCategory": "Women",
        "tags": "Women, SHG, Lakhpati Didi, Micro Enterprise, Self Help Group, Business Loan, Rural Women",
        "deadline": "Open Year Round"
    },
    {
        "scheme_name": "PM Matsya Sampada 2.0: Deep Sea Fishing & Aquaculture Subsidy",
        "slug": "pm-matsya-sampada-aquaculture-2026",
        "details": "Financial assistance program for fishermen, fish farmers, and bio-floc aquaculture entrepreneurs to modernize inland and coastal fisheries infrastructure.",
        "benefits": "60% financial subsidy for Women and SC/ST beneficiaries, 40% for General beneficiaries on capital cost of fish ponds, bio-floc units, motor boats, and cold-chain transport vehicles.",
        "eligibility": "Individual fishermen, fish farmers, Women SHGs, Fish Tenant Farmers, and Marine Fisheries Cooperatives.",
        "application": "Submit project proposal on NFDB portal (pmmsy.dof.gov.in) or to District Fisheries Office.",
        "documents": "Aadhaar Card, Land Lease / Waterbody Permission, Bank Passbook, Fisheries Registration",
        "level": "Central",
        "schemeCategory": "Farmers",
        "tags": "Fisheries, Fish Farming, PMMSY, Subsidy, Aqua Culture, Boat, Marine, Fisherman",
        "deadline": "2026-11-30"
    }
]


class SchemeCollectorService:
    """
    Automated Scheme Collector Engine for JanSathi AI.
    Daily syncs relevant current & upcoming government schemes into SQLite database.
    """

    def __init__(self):
        self.last_sync_time: str = ""
        self.last_sync_count: int = 0

    def sync_latest_schemes(self, db: Session) -> Dict[str, Any]:
        """
        Synchronize latest relevant daily schemes into SQLite database without duplicates.
        """
        # Fetch existing schemes to avoid duplicate entries
        existing_schemes = db.query(Scheme).all()
        existing_keys = set()
        for s in existing_schemes:
            name = (s.scheme_name or s.title_legacy or "").strip().lower()
            slug = (s.slug or "").strip().lower()
            if name:
                existing_keys.add((name, slug))

        added_count = 0
        added_titles = []

        for item in LATEST_GOVT_SCHEMES:
            name = item["scheme_name"].strip()
            slug = item["slug"].strip()
            key = (name.lower(), slug.lower())

            if key not in existing_keys:
                new_scheme = Scheme(
                    scheme_name=name,
                    slug=slug,
                    details=item["details"],
                    benefits=item["benefits"],
                    eligibility=item["eligibility"],
                    application=item["application"],
                    documents=item["documents"],
                    level=item["level"],
                    schemeCategory=item["schemeCategory"],
                    tags=item["tags"],
                    title_legacy=name,
                    category_legacy=item["schemeCategory"],
                    description_legacy=item["details"],
                    required_documents_legacy=item["documents"],
                    deadline=item.get("deadline", "Open Year Round")
                )
                db.add(new_scheme)
                existing_keys.add(key)
                added_count += 1
                added_titles.append(name)

        if added_count > 0:
            db.commit()
            logger.info(f"[Daily Scheme Sync] Successfully added {added_count} new government schemes to database.")

        total_db_schemes = db.query(Scheme).count()
        self.last_sync_time = datetime.datetime.now().isoformat()
        self.last_sync_count = added_count

        return {
            "status": "success",
            "message": f"Daily government scheme sync completed. Added {added_count} new scheme(s).",
            "new_schemes_added": added_count,
            "new_scheme_titles": added_titles,
            "total_schemes_in_db": total_db_schemes,
            "last_sync_time": self.last_sync_time
        }


# Singleton instance
scheme_collector = SchemeCollectorService()

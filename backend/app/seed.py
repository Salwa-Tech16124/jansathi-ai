from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.models.citizen import Citizen
from app.models.reminder import Reminder

SEED_SCHEMES = [
    {
        "title": "National Means-cum-Merit Scholarship (NMMSS)",
        "category": "Scholarships",
        "description": "Financial assistance of ₹12,000 per annum to meritorious students of economically weaker sections to arrest dropouts at class VIII.",
        "eligibility": "Students studying in Class IX with minimum 55% marks in Class VIII. Parental annual income must not exceed ₹3,500,000.",
        "required_documents": "Aadhaar Card, Class VIII Marksheet, Income Certificate, Caste Certificate, Bank Account Details",
        "deadline": "2026-10-31"
    },
    {
        "title": "Post-Matric Scholarship for SC/ST Students",
        "category": "Scholarships",
        "description": "Provides financial support to Scheduled Caste and Scheduled Tribe students studying at post-matriculation or post-secondary stage.",
        "eligibility": "SC/ST students studying in Class XI up to PhD level in recognized institutions with family income under ₹2.5 Lakh per annum.",
        "required_documents": "Caste Certificate, Income Certificate, Aadhaar Card, Fee Receipt, Previous Year Marksheet",
        "deadline": "2026-11-30"
    },
    {
        "title": "PM-Kisan Samman Nidhi Yojana",
        "category": "Farmers",
        "description": "Direct income support of ₹6,000 per year paid in three equal installments of ₹2,000 directly into the bank accounts of landholding farmer families.",
        "eligibility": "Small and marginal landholder farmer families owning cultivable land up to 2 hectares across India.",
        "required_documents": "Land Ownership Record (Khata/Khatian), Aadhaar Card, Bank Passbook, Land Revenue Receipt",
        "deadline": "Open Year Round"
    },
    {
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Farmers",
        "description": "Comprehensive crop insurance coverage against non-preventable natural risks, pests, and diseases to stabilize farmers' income.",
        "eligibility": "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas.",
        "required_documents": "Sowing Certificate/Land Lease Agreement, Aadhaar Card, Bank Account Passbook, Land Record Document",
        "deadline": "2026-08-31"
    },
    {
        "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "category": "Women",
        "description": "Direct Benefit Transfer (DBT) scheme providing financial incentive of ₹5,000 in two installments for pregnant women and lactating mothers.",
        "eligibility": "Pregnant Women and Lactating Mothers (PW&LM) for the first and second child (if second child is female).",
        "required_documents": "Mother and Child Protection (MCP) Card, Aadhaar Card of Mother and Husband, Bank Account Details",
        "deadline": "Open Year Round"
    },
    {
        "title": "Lakhpati Didi Scheme",
        "category": "Women",
        "description": "Skill development training, financial literacy, and micro-entrepreneurship support to empower women in Self-Help Groups (SHGs) to earn at least ₹1 Lakh per year.",
        "eligibility": "Women members associated with recognized Self-Help Groups (SHGs) under Deendayal Antyodaya Yojana - NRLM.",
        "required_documents": "SHG Membership Proof, Aadhaar Card, Bank Passbook, Passport Size Photograph",
        "deadline": "Open Year Round"
    },
    {
        "title": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "category": "Senior Citizens",
        "description": "Monthly pension assistance provided to senior citizens living below the poverty line to ensure dignified financial independence.",
        "eligibility": "Citizens aged 60 years and above belonging to households below the poverty line (BPL).",
        "required_documents": "BPL Card, Age Proof (Aadhaar Card / Voter ID), Bank Account Passbook, Residence Certificate",
        "deadline": "Open Year Round"
    },
    {
        "title": "Pradhan Mantri Vaya Vandana Yojana (PMVVY)",
        "category": "Senior Citizens",
        "description": "Pension scheme operated through LIC providing assured return of up to 7.4% per annum for 10 years to senior citizens.",
        "eligibility": "Indian senior citizens aged 60 years and above. Maximum investment limit is ₹15 Lakh per senior citizen.",
        "required_documents": "Aadhaar Card, PAN Card, Bank Account Details for NEFT, Proof of Age",
        "deadline": "2026-12-31"
    },
    {
        "title": "Ayushman Bharat - PM-JAY",
        "category": "Health",
        "description": "World's largest health insurance scheme providing cashless health cover up to ₹5 Lakh per family per year for secondary and tertiary care hospitalization.",
        "eligibility": "Low-income families identified based on SECC 2011 data and senior citizens aged 70 and above regardless of income.",
        "required_documents": "Aadhaar Card / Ration Card, Ayushman Card (or e-KYC via mobile app)",
        "deadline": "Open Year Round"
    },
    {
        "title": "National Health Mission - Free Diagnostic & Medicine Service",
        "category": "Health",
        "description": "Ensures free essential drugs and diagnostic services at all public health facilities including PHCs, CHCs, and District Hospitals.",
        "eligibility": "All citizens visiting government healthcare centers, clinics, and hospitals.",
        "required_documents": "Doctor Prescription from Government Hospital, Government ID Proof",
        "deadline": "Open Year Round"
    }
]


def seed_database(db: Session):
    """
    Populate database with initial 10 realistic government schemes and default demo citizen with reminders.
    """
    # Seed Schemes if empty
    existing_schemes = db.query(Scheme).count()
    if existing_schemes == 0:
        for s in SEED_SCHEMES:
            db.add(Scheme(**s))
        db.commit()
        print("[SEED] Successfully seeded 10 government schemes.")

    # Seed Default Citizen if empty
    existing_citizens = db.query(Citizen).count()
    if existing_citizens == 0:
        demo_citizen = Citizen(
            name="Rajesh Kumar",
            phone="9876543210",
            language="Hindi",
            district="Lakhimpur Kheri",
            state="Uttar Pradesh"
        )
        db.add(demo_citizen)
        db.commit()
        db.refresh(demo_citizen)
        print("[SEED] Successfully seeded demo citizen.")

        # Seed initial reminders for demo citizen
        pm_kisan = db.query(Scheme).filter(Scheme.title.like("%PM-Kisan%")).first()
        pension = db.query(Scheme).filter(Scheme.title.like("%Old Age Pension%")).first()
        ayushman = db.query(Scheme).filter(Scheme.title.like("%Ayushman Bharat%")).first()

        reminders = [
            Reminder(
                citizen_id=demo_citizen.id,
                scheme_id=pension.id if pension else None,
                title="Submit Annual Life Certificate for Pension",
                category="Senior Citizens",
                reminder_date="2026-11-30",
                status="pending"
            ),
            Reminder(
                citizen_id=demo_citizen.id,
                scheme_id=pm_kisan.id if pm_kisan else None,
                title="Verify PM-Kisan e-KYC & Land Seeding",
                category="Farmers",
                reminder_date="2026-08-15",
                status="pending"
            ),
            Reminder(
                citizen_id=demo_citizen.id,
                scheme_id=ayushman.id if ayushman else None,
                title="Renew Ayushman Card for Family",
                category="Health",
                reminder_date="2026-07-30",
                status="completed"
            )
        ]
        db.add_all(reminders)
        db.commit()
        print("[SEED] Successfully seeded default citizen reminders.")

from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.models.citizen import Citizen
from app.models.reminder import Reminder

SEED_SCHEMES = [
    # 🎓 1. Education & Scholarships
    {
        "title": "National Means-cum-Merit Scholarship (NMMSS)",
        "category": "Scholarships",
        "description": "Financial assistance of ₹12,000 per annum to meritorious students of economically weaker sections to arrest dropouts at class VIII.",
        "eligibility": "Students studying in Class IX with minimum 55% marks in Class VIII. Parental annual income must not exceed ₹3.5 Lakh.",
        "required_documents": "Aadhaar Card, Class VIII Marksheet, Income Certificate, Caste Certificate, Bank Account Passbook",
        "deadline": "2026-10-31"
    },
    {
        "title": "Post-Matric Scholarship for SC/ST/OBC Students",
        "category": "Scholarships",
        "description": "Provides tuition fee coverage and maintenance allowance to SC/ST/OBC students studying at post-secondary levels.",
        "eligibility": "SC/ST/OBC students studying in Class XI up to PhD level in recognized institutions with annual family income under ₹2.5 Lakh.",
        "required_documents": "Caste Certificate, Income Certificate, Aadhaar Card, Institute Fee Receipt, Previous Year Marksheet",
        "deadline": "2026-11-30"
    },
    {
        "title": "PM Vidyalaxmi Higher Education Loan Scheme",
        "category": "Scholarships",
        "description": "Collateral-free education loans up to ₹10 Lakh with 7.5% interest subvention for meritorious students pursuing higher studies in top Indian institutes.",
        "eligibility": "Students admitted to top 860 quality higher education institutions in India. Annual family income under ₹8 Lakh.",
        "required_documents": "Admission Letter, Course Fee Structure, Aadhaar Card, PAN Card, Income Proof",
        "deadline": "Open Year Round"
    },
    {
        "title": "Central Sector Scheme of Scholarships for College Students",
        "category": "Scholarships",
        "description": "Financial support of ₹12,000 to ₹20,000 per year to top 80th percentile students passing Class XII for undergraduate and postgraduate courses.",
        "eligibility": "Class XII passed students pursuing regular degree courses with family income below ₹4.5 Lakh per annum.",
        "required_documents": "Class XII Marksheet, Income Certificate, College Enrollment Proof, Aadhaar Card, Bank Passbook",
        "deadline": "2026-12-15"
    },

    # 👨‍🌾 2. Farmers & Agriculture
    {
        "title": "PM-Kisan Samman Nidhi Yojana",
        "category": "Farmers",
        "description": "Direct income support of ₹6,000 per year paid in three equal installments of ₹2,000 directly into the bank accounts of landholding farmers.",
        "eligibility": "Small and marginal landholder farmer families owning cultivable land up to 2 hectares across India.",
        "required_documents": "Land Ownership Record (Khata/Khatian), Aadhaar Card, Bank Passbook, e-KYC Verification",
        "deadline": "Open Year Round"
    },
    {
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Farmers",
        "description": "Comprehensive insurance coverage against crop loss due to droughts, floods, pests, and natural hazards to stabilize farmer income.",
        "eligibility": "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas.",
        "required_documents": "Sowing Certificate/Land Lease Agreement, Aadhaar Card, Bank Passbook, Land Revenue Record",
        "deadline": "2026-08-31"
    },
    {
        "title": "Kisan Credit Card (KCC) Scheme",
        "category": "Farmers",
        "description": "Timely short-term credit facility for agricultural inputs (seeds, fertilizers) and animal husbandry at a subsidized interest rate of 4%.",
        "eligibility": "Individual/joint farmers, tenant farmers, oral lessees, and self-help groups engaged in farming or dairy.",
        "required_documents": "Land Records, Passport Size Photograph, Aadhaar Card, Bank Account Details",
        "deadline": "Open Year Round"
    },
    {
        "title": "PM Krishi Sinchayee Yojana (Micro Irrigation)",
        "category": "Farmers",
        "description": "Financial subsidy of up to 55% for installing drip and sprinkler irrigation systems to maximize water use efficiency ('More Crop Per Drop').",
        "eligibility": "Farmers owning cultivable land with adequate water source. Preference to small and marginal farmers.",
        "required_documents": "Land Title Document, Aadhaar Card, Bank Passbook, Soil & Water Testing Report",
        "deadline": "2026-09-30"
    },

    # 👩 3. Women Welfare
    {
        "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "category": "Women",
        "description": "Direct Benefit Transfer (DBT) incentive of ₹5,000 to ₹6,000 for pregnant women and lactating mothers for health and nutrition.",
        "eligibility": "Pregnant women and lactating mothers for their first child, and an additional ₹6,000 if the second child is a girl.",
        "required_documents": "Mother & Child Protection (MCP) Card, Aadhaar Card of Mother & Husband, Bank Account Details",
        "deadline": "Open Year Round"
    },
    {
        "title": "Lakhpati Didi Scheme",
        "category": "Women",
        "description": "Skill development, micro-enterprise training, and credit linkage for Self-Help Group (SHG) women to enable an annual income of at least ₹1 Lakh.",
        "eligibility": "Women associated with recognized Self-Help Groups under DAY-NRLM in rural and semi-urban areas.",
        "required_documents": "SHG Passbook, Aadhaar Card, Bank Account Passbook, Passport Size Photograph",
        "deadline": "Open Year Round"
    },
    {
        "title": "Sukanya Samriddhi Yojana (SSY)",
        "category": "Women",
        "description": "High-interest tax-exempt savings scheme for girl children offering 8.2% annual interest to secure education and marriage funds.",
        "eligibility": "Parents or legal guardians of a girl child below 10 years of age. Maximum two girl children per family.",
        "required_documents": "Girl Child Birth Certificate, Aadhaar Card of Parent/Guardian, Address Proof, Initial Deposit",
        "deadline": "Open Year Round"
    },
    {
        "title": "Pradhan Mantri Ujjwala Yojana 2.0",
        "category": "Women",
        "description": "Free LPG gas connection with first refill and stove provided free of cost to adult women from low-income households.",
        "eligibility": "Adult woman belonging to BPL/poor households without any existing LPG connection in the family.",
        "required_documents": "Ration Card, Aadhaar Card of all family members, Bank Passbook, Address Proof",
        "deadline": "Open Year Round"
    },

    # 👴 4. Senior Citizens
    {
        "title": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "category": "Senior Citizens",
        "description": "Monthly pension assistance provided to senior citizens living below the poverty line to ensure dignified financial security.",
        "eligibility": "Citizens aged 60 years and above belonging to BPL households (₹200/mo for 60-79 yrs; ₹500/mo for 80+ yrs).",
        "required_documents": "BPL Ration Card, Aadhaar Card / Age Proof, Bank Passbook, Residence Certificate",
        "deadline": "Open Year Round"
    },
    {
        "title": "Pradhan Mantri Vaya Vandana Yojana (PMVVY)",
        "category": "Senior Citizens",
        "description": "Guaranteed pension scheme operated via LIC providing an assured return of up to 7.4% per annum for 10 years to senior citizens.",
        "eligibility": "Indian senior citizens aged 60 years and above. Maximum investment limit is ₹15 Lakh per individual.",
        "required_documents": "Aadhaar Card, PAN Card, Bank Account Passbook, Proof of Age",
        "deadline": "2026-12-31"
    },
    {
        "title": "Rashtriya Vayoshri Yojana (RVY)",
        "category": "Senior Citizens",
        "description": "Free distribution of physical aids and assisted-living devices (wheelchairs, hearing aids, walking sticks, spectacles) for senior citizens.",
        "eligibility": "Senior citizens aged 60+ belonging to BPL category or monthly family income under ₹15,000.",
        "required_documents": "Age Proof, BPL Card / Income Certificate, Aadhaar Card, Medical Certificate for Disability/Impairment",
        "deadline": "Open Year Round"
    },

    # 🏥 5. Health
    {
        "title": "Ayushman Bharat - PM-JAY",
        "category": "Health",
        "description": "Cashless health insurance coverage up to ₹5 Lakh per family per year for secondary and tertiary care hospitalization in empaneled hospitals.",
        "eligibility": "Low-income families identified in SECC 2011 data, and ALL senior citizens aged 70+ regardless of income.",
        "required_documents": "Aadhaar Card, Ration Card / Family ID, Ayushman Card (e-KYC)",
        "deadline": "Open Year Round"
    },
    {
        "title": "PM Bharatiya Janaushadhi Pariyojana",
        "category": "Health",
        "description": "Access to high-quality generic medicines, surgical items, and nutraceuticals at 50% to 90% lower prices than branded medicines.",
        "eligibility": "Open to all citizens across Jan Aushadhi Kendras in India.",
        "required_documents": "Doctor's Prescription (No ID mandatory for OTC purchase)",
        "deadline": "Open Year Round"
    },
    {
        "title": "National Health Mission - Free Diagnostics & Drugs",
        "category": "Health",
        "description": "Free essential medicines and diagnostic blood/radiology tests across primary and district government hospitals.",
        "eligibility": "All patients visiting Government PHCs, CHCs, and District Hospitals.",
        "required_documents": "Government Hospital Prescription / OP Slip",
        "deadline": "Open Year Round"
    },

    # 🏠 6. Housing
    {
        "title": "Pradhan Mantri Awas Yojana - Gramin (PMAY-G)",
        "category": "Housing",
        "description": "Financial assistance of ₹1.2 Lakh to ₹1.3 Lakh for constructing pucca houses with basic amenities for homeless rural families.",
        "eligibility": "Homeless rural households or living in kutcha/damaged houses identified via SECC data.",
        "required_documents": "Job Card Number, Aadhaar Card, Bank Passbook, Land Ownership Proof / NOC",
        "deadline": "Open Year Round"
    },
    {
        "title": "Pradhan Mantri Awas Yojana - Urban (PMAY-U 2.0)",
        "category": "Housing",
        "description": "Interest subsidy up to ₹2.67 Lakh on home loans for urban middle-income (MIG) and economically weaker (EWS) families.",
        "eligibility": "Urban families not owning a pucca house anywhere in India. Annual household income up to ₹18 Lakh.",
        "required_documents": "Aadhaar Card, Income Certificate, Home Loan Approval Letter, Property Purchase Agreement",
        "deadline": "2026-12-31"
    },

    # 💼 7. Employment & Skill Development
    {
        "title": "MGNREGA (Mahatma Gandhi National Rural Employment Guarantee)",
        "category": "Employment",
        "description": "Legal guarantee of at least 100 days of wage employment per financial year to rural adult household members willing to do manual work.",
        "eligibility": "Adult members of any rural household willing to undertake unskilled manual labor.",
        "required_documents": "Rural Job Card, Aadhaar Card, Bank/Post Office Account Details",
        "deadline": "Open Year Round"
    },
    {
        "title": "PM Kaushal Vikas Yojana 4.0 (PMKVY)",
        "category": "Employment",
        "description": "Free industry-relevant skill training, certification, and job placement assistance along with a stipend for unemployed youth.",
        "eligibility": "Indian youth aged 15 to 45 years who are unemployed or school/college dropouts.",
        "required_documents": "Aadhaar Card, Educational Certificates, Bank Passbook, Passport Photo",
        "deadline": "Open Year Round"
    },
    {
        "title": "PM-Vishwakarma Yojana",
        "category": "Employment",
        "description": "Collateral-free credit up to ₹3 Lakh at 5% interest, toolkits worth ₹15,000, and skill training for traditional artisans and craftsmen.",
        "eligibility": "Artisans/craftspeople working with hands/tools across 18 traditional trades (carpenters, blacksmiths, tailors, potters, etc.).",
        "required_documents": "Aadhaar Card, Ration Card, Skill Trade Declaration, Bank Account Passbook",
        "deadline": "Open Year Round"
    },

    # 🏭 8. MSME / Business
    {
        "title": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "category": "Business",
        "description": "Collateral-free business loans up to ₹20 Lakh (Shishu: ₹50k, Kishor: ₹5 Lakh, Tarun: ₹20 Lakh) for micro and small non-farm enterprises.",
        "eligibility": "Small business owners, shopkeepers, fruit vendors, artisans, and micro-manufacturers.",
        "required_documents": "Business Plan/Proposal, Aadhaar Card, PAN Card, Bank Statement of last 6 months, Business Address Proof",
        "deadline": "Open Year Round"
    },
    {
        "title": "PM Employment Generation Programme (PMEGP)",
        "category": "Business",
        "description": "Credit-linked subsidy program offering up to 35% margin money subsidy for setting up new micro-manufacturing/service projects up to ₹50 Lakh.",
        "eligibility": "Individuals above 18 years of age. Minimum 8th class pass for projects above ₹10 Lakh in manufacturing.",
        "required_documents": "Detailed Project Report (DPR), Educational Certificate, Caste Certificate, Aadhaar Card, Bank Passbook",
        "deadline": "Open Year Round"
    },
    {
        "title": "Stand-Up India Scheme",
        "category": "Business",
        "description": "Bank loans between ₹10 Lakh and ₹1 Crore for setting up greenfield enterprises in manufacturing, services, or trading by SC/ST/Women.",
        "eligibility": "SC/ST and/or Woman entrepreneurs above 18 years of age setting up a new business.",
        "required_documents": "Identity Proof, Caste/Category Certificate, Business Registration, Project Report, Lease/Land Document",
        "deadline": "Open Year Round"
    },

    # ♿ 9. Persons with Disabilities (Divyangjan)
    {
        "title": "Indira Gandhi National Disability Pension Scheme (IGNDPS)",
        "category": "Disability",
        "description": "Monthly pension assistance of ₹500 to ₹1,000 for persons with severe or multiple disabilities belonging to BPL households.",
        "eligibility": "Persons aged 18 years and above with 80% or higher disability belonging to BPL families.",
        "required_documents": "Disability Certificate (UDID), BPL Ration Card, Aadhaar Card, Bank Account Details",
        "deadline": "Open Year Round"
    },
    {
        "title": "ADIP Scheme (Assistance to Disabled Persons for Aids & Appliances)",
        "category": "Disability",
        "description": "Free distribution of durable, modern aids and assistive devices (wheelchairs, motorized tricycles, braille kits, hearing aids).",
        "eligibility": "Indian citizens with 40%+ certified disability and monthly income under ₹20,000 (free) or up to ₹40,000 (50% subsidy).",
        "required_documents": "UDID Disability Certificate, Income Certificate, Aadhaar Card, Residence Proof",
        "deadline": "Open Year Round"
    },
    {
        "title": "National Fellowship / Scholarship for Students with Disabilities",
        "category": "Disability",
        "description": "Financial assistance and maintenance allowance for students with disabilities to pursue graduate and post-graduate studies.",
        "eligibility": "Students with 40%+ disability pursuing post-matriculation or higher education with family income under ₹6 Lakh per annum.",
        "required_documents": "UDID Card, Educational Certificates, Income Certificate, Aadhaar Card, Bank Passbook",
        "deadline": "2026-11-15"
    },

    # 👶 10. Child Welfare
    {
        "title": "PM CARES for Children Scheme",
        "category": "Child Welfare",
        "description": "Comprehensive care, health insurance of ₹5 Lakh under PM-JAY, monthly stipend, and ₹10 Lakh corpus fund upon reaching 23 years of age for pandemic orphans.",
        "eligibility": "Children who lost both parents or surviving parent due to COVID-19 pandemic before turning 18 years.",
        "required_documents": "Death Certificate of Parents, Child Birth Certificate, Aadhaar Card, Guardian Details",
        "deadline": "Open Year Round"
    },
    {
        "title": "Mission Vatsalya (Child Protection & Rehabilitation Services)",
        "category": "Child Welfare",
        "description": "Sponsorship, foster care support of ₹4,000 per month per child, and institutional shelter for vulnerable children in need of care.",
        "eligibility": "Orphan, abandoned, single-parent, or child in vulnerable circumstances with family income under ₹72,000 (rural) / ₹96,000 (urban).",
        "required_documents": "Child Age Proof, Income Certificate of Guardian, Aadhaar Card, CWC Order",
        "deadline": "Open Year Round"
    },
    {
        "title": "Integrated Child Development Services (ICDS / Poshan 2.0)",
        "category": "Child Welfare",
        "description": "Supplementary nutrition, immunization, health check-up, and preschool education for children below 6 years at Anganwadi centers.",
        "eligibility": "All children aged 0 to 6 years, pregnant women, and lactating mothers.",
        "required_documents": "Anganwadi Registration, Aadhaar Card of Mother/Child, Birth Certificate",
        "deadline": "Open Year Round"
    }
]


def seed_database(db: Session):
    """
    Populate database with 30+ realistic government schemes across 10 citizen categories.
    """
    existing_schemes = db.query(Scheme).all()
    existing_titles = {s.title for s in existing_schemes}

    added_count = 0
    for s in SEED_SCHEMES:
        if s["title"] not in existing_titles:
            db.add(Scheme(**s))
            added_count += 1

    if added_count > 0:
        db.commit()
        print(f"[SEED] Successfully seeded {added_count} new government schemes across 10 citizen categories.")

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
        pension = db.query(Scheme).filter(Scheme.category == "Senior Citizens").first()
        farmer = db.query(Scheme).filter(Scheme.category == "Farmers").first()
        health = db.query(Scheme).filter(Scheme.category == "Health").first()

        reminders = [
            Reminder(
                citizen_id=demo_citizen.id,
                scheme_id=pension.id if pension else None,
                title="Submit Annual Life Certificate for Pension (Jeevan Pramaan)",
                category="Senior Citizens",
                reminder_date="2026-11-30",
                status="pending"
            ),
            Reminder(
                citizen_id=demo_citizen.id,
                scheme_id=farmer.id if farmer else None,
                title="PM-Kisan e-KYC & Land Seeding Deadline",
                category="Farmers",
                reminder_date="2026-08-15",
                status="pending"
            ),
            Reminder(
                citizen_id=demo_citizen.id,
                scheme_id=health.id if health else None,
                title="Renew Ayushman Bharat Golden Card for Family",
                category="Health",
                reminder_date="2026-07-30",
                status="completed"
            )
        ]
        db.add_all(reminders)
        db.commit()
        print("[SEED] Successfully seeded default citizen reminders.")

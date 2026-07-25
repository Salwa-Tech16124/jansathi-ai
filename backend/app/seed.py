import csv
import os
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.models.citizen import Citizen
from app.models.reminder import Reminder

logger = logging.getLogger("jansathi.seed")

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "updated_data.csv")


def migrate_schemes_table(db: Session):
    """
    Auto-migrate SQLite 'schemes' table if it already exists,
    adding any missing columns safely without dropping data.
    """
    try:
        engine = db.get_bind()
        with engine.connect() as conn:
            # Check existing columns in schemes table
            res = conn.execute(text("PRAGMA table_info(schemes);")).fetchall()
            if not res:
                return  # Table doesn't exist yet, create_all will handle it
            
            existing_cols = {row[1] for row in res}
            needed_cols = {
                "scheme_name": "TEXT",
                "slug": "TEXT",
                "details": "TEXT",
                "benefits": "TEXT",
                "eligibility": "TEXT",
                "application": "TEXT",
                "documents": "TEXT",
                "level": "TEXT",
                "schemeCategory": "TEXT",
                "tags": "TEXT",
            }
            
            for col_name, col_type in needed_cols.items():
                if col_name not in existing_cols:
                    logger.info(f"[MIGRATION] Adding missing column '{col_name}' to schemes table.")
                    conn.execute(text(f'ALTER TABLE schemes ADD COLUMN "{col_name}" {col_type};'))
            conn.commit()
    except Exception as err:
        logger.warning(f"[MIGRATION] Table migration notice: {err}")


def import_csv_dataset(db: Session):
    """
    Step 1: Automatically detect CSV structure, validate rows, ignore duplicates,
    and import all scheme records into SQLite with required indexes.
    """
    # 1. Run migration to ensure all new columns exist in SQLite table
    migrate_schemes_table(db)

    csv_file = os.path.abspath(CSV_PATH)
    if not os.path.exists(csv_file):
        logger.warning(f"[SEED] CSV dataset file not found at {csv_file}")
        return

    # 2. Read existing schemes to prevent duplicates
    existing_schemes = db.query(Scheme).all()
    seen_keys = set()
    for s in existing_schemes:
        name = (s.scheme_name or s.title_legacy or "").strip().lower()
        slug = (s.slug or "").strip().lower()
        if name:
            seen_keys.add((name, slug))

    total_rows = 0
    imported_rows = 0
    duplicate_rows_skipped = 0
    invalid_rows_skipped = 0

    new_schemes = []

    with open(csv_file, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            print("[SEED] CSV file is empty.")
            return

        for row in reader:
            total_rows += 1
            if not row or len(row) < 1 or not row[0].strip():
                invalid_rows_skipped += 1
                continue

            scheme_name = row[0].strip()
            slug = row[1].strip() if len(row) > 1 else ""
            details = row[2].strip() if len(row) > 2 else ""
            benefits = row[3].strip() if len(row) > 3 else ""
            eligibility = row[4].strip() if len(row) > 4 else ""
            application = row[5].strip() if len(row) > 5 else ""
            documents = row[6].strip() if len(row) > 6 else ""
            level = row[7].strip() if len(row) > 7 else ""
            scheme_category = row[8].strip() if len(row) > 8 else ""

            tags = ""
            if len(row) >= 11:
                tags = row[10].strip()
            elif len(row) == 10:
                tags = row[9].strip()

            key = (scheme_name.lower(), slug.lower())
            if key in seen_keys:
                duplicate_rows_skipped += 1
                continue

            seen_keys.add(key)

            new_scheme = Scheme(
                scheme_name=scheme_name,
                slug=slug,
                details=details,
                benefits=benefits,
                eligibility=eligibility,
                application=application,
                documents=documents,
                level=level,
                schemeCategory=scheme_category,
                tags=tags,
                title_legacy=scheme_name,
                category_legacy=scheme_category or "General Welfare",
                description_legacy=details,
                required_documents_legacy=documents,
                deadline="Open Year Round"
            )
            new_schemes.append(new_scheme)
            imported_rows += 1

            if len(new_schemes) >= 500:
                db.bulk_save_objects(new_schemes)
                db.commit()
                new_schemes = []

    if new_schemes:
        db.bulk_save_objects(new_schemes)
        db.commit()

    print("\n==========================================")
    print("      DATASET IMPORT SUMMARY")
    print("==========================================")
    print(f"- Total rows: {total_rows}")
    print(f"- Imported rows: {imported_rows}")
    print(f"- Duplicate rows skipped: {duplicate_rows_skipped}")
    print(f"- Invalid rows skipped: {invalid_rows_skipped}")
    print("==========================================\n")

    # Create Indexes on scheme_name, schemeCategory, tags
    try:
        engine = db.get_bind()
        with engine.connect() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_scheme_name ON schemes (scheme_name);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_scheme_category ON schemes (schemeCategory);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tags ON schemes (tags);"))
            conn.commit()
    except Exception as e:
        logger.warning(f"[SEED] Index creation notice: {e}")


def seed_database(db: Session):
    """
    Main database import and seed entry point.
    Runs CSV import first, then ensures demo citizen and initial reminders exist.
    """
    import_csv_dataset(db)

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
        pension = db.query(Scheme).filter(Scheme.schemeCategory.ilike("%Senior%") | Scheme.tags.ilike("%pension%")).first()
        farmer = db.query(Scheme).filter(Scheme.schemeCategory.ilike("%Agri%") | Scheme.tags.ilike("%farmer%")).first()
        health = db.query(Scheme).filter(Scheme.schemeCategory.ilike("%Health%") | Scheme.tags.ilike("%health%")).first()

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

"""
Seeds the starting set of forums. Run once per fresh database:
    python seed.py
Idempotent -- safe to run again, existing forums (matched by slug) are skipped.
"""
from app.database import SessionLocal
from app.models import Forum

FORUMS = [
    ("Placement Prep", "placement-prep", "Ask peers about specific companies, interview rounds, and prep strategy."),
    ("Computer Science", "cs-dept", "Department-wide discussion for CS students."),
    ("Electronics & Comm.", "ece-dept", "Department-wide discussion for ECE students."),
    ("Hackathons", "hackathons", "Announce hackathons and coordinate outside the project board."),
]


def run():
    db = SessionLocal()
    try:
        created = 0
        for name, slug, description in FORUMS:
            if db.query(Forum).filter_by(slug=slug).first() is None:
                db.add(Forum(name=name, slug=slug, description=description))
                created += 1
        db.commit()
        print(f"Seeded {created} new forum(s); {len(FORUMS) - created} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()

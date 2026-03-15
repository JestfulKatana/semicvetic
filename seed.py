from app import create_app
from app.demo_seed import seed_database
from app.extensions import db


app = create_app()

with app.app_context():
    db.create_all()
    seed_database()
    print("Seed completed")

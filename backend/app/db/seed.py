import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
from datetime import datetime, timedelta
from app.db.session import engine, SessionLocal, Base
from app.db.models import (
    Store, User, Department, Employee, Shift,
    FootfallData, QueueData, CameraEvent, Prediction, Recommendation
)
from app.core.security import get_password_hash

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded.")
            return

        print("Seeding RetailSense AI database with realistic retail enterprise data...")

        # 1. Create Main Flagship Store
        store = Store(
            name="RetailSense Flagship Store #101",
            location="742 Evergreen Terrace, Tech District",
            city="Metropolis",
            sqft=25000
        )
        db.add(store)
        db.commit()
        db.refresh(store)

        # 2. Create Users with RBAC
        admin_user = User(
            name="Alexander Vance (Admin)",
            email="admin@retailsense.ai",
            password_hash=get_password_hash("AdminSecret123!"),
            role="Admin",
            store_id=store.id
        )
        manager_user = User(
            name="Sarah Jenkins (Store Manager)",
            email="manager@retailsense.ai",
            password_hash=get_password_hash("Manager123!"),
            role="Manager",
            store_id=store.id
        )
        employee_user = User(
            name="David Miller (Team Lead)",
            email="employee@retailsense.ai",
            password_hash=get_password_hash("Employee123!"),
            role="Employee",
            store_id=store.id
        )
        db.add_all([admin_user, manager_user, employee_user])
        db.commit()

        # 3. Create Departments
        departments_data = [
            ("Grocery & Produce", 8),
            ("Apparel & Fashion", 6),
            ("Electronics & Appliances", 4),
            ("Checkout & Cashier Ops", 10),
            ("Security & Facilities", 4)
        ]
        dept_objects = {}
        for dept_name, target in departments_data:
            dept = Department(store_id=store.id, name=dept_name, target_staff=target)
            db.add(dept)
            db.commit()
            db.refresh(dept)
            dept_objects[dept_name] = dept

        # 4. Create Employees
        roles_distribution = [
            ("Checkout & Cashier Ops", "Cashier", 12, 220.00),
            ("Grocery & Produce", "Sales Associate", 8, 250.00),
            ("Apparel & Fashion", "Sales Associate", 6, 260.00),
            ("Electronics & Appliances", "Tech Specialist", 4, 350.00),
            ("Security & Facilities", "Security Guard", 4, 200.00),
        ]
        
        emp_id_counter = 1
        for dept_name, role_title, count, rate in roles_distribution:
            dept = dept_objects[dept_name]
            for i in range(1, count + 1):
                emp = Employee(
                    store_id=store.id,
                    department_id=dept.id,
                    name=f"{role_title} Staff {emp_id_counter}",
                    role=role_title,
                    hourly_rate=rate,
                    status="Active"
                )
                db.add(emp)
                emp_id_counter += 1
        db.commit()

        # 5. Generate Historical Hourly Footfall Data (Last 90 Days)
        print("Generating 90 days of synthetic hourly footfall & environmental telemetry...")
        now = datetime.utcnow()
        start_date = now - timedelta(days=90)
        
        footfall_records = []
        queue_records = []
        
        current_time = start_date.replace(minute=0, second=0, microsecond=0)
        while current_time <= now:
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # Store open hours: 8 AM to 10 PM
            if 8 <= hour <= 22:
                # Realistic traffic curve: peak at lunch (12-2 PM) and evening (5-8 PM)
                base_count = 50
                if 12 <= hour <= 14:
                    base_count = 280
                elif 17 <= hour <= 20:
                    base_count = 350
                elif 8 <= hour <= 10:
                    base_count = 90
                
                # Weekend multiplier
                is_weekend = day_of_week >= 5
                weekend_mult = 1.45 if is_weekend else 1.0
                
                # Random fluctuations + promotion/holiday noise
                is_holiday = random.random() < 0.05
                is_promo = random.random() < 0.15
                
                multiplier = weekend_mult * (1.3 if is_holiday else 1.0) * (1.2 if is_promo else 1.0)
                final_count = int(base_count * multiplier + random.randint(-20, 25))
                final_count = max(10, final_count)

                temp = round(20.0 + random.uniform(-4, 6), 1)
                rain = round(random.uniform(0, 15), 1) if random.random() < 0.2 else 0.0

                ff = FootfallData(
                    store_id=store.id,
                    timestamp=current_time,
                    count=final_count,
                    temperature=temp,
                    rain_mm=rain,
                    is_holiday=is_holiday,
                    promotion_active=is_promo,
                    hour=hour,
                    day_of_week=day_of_week
                )
                footfall_records.append(ff)

                # Queue metric estimation
                active_counters = min(10, max(2, int(final_count / 35)))
                avg_queue_len = max(1, int(final_count / (active_counters * 12)))
                wait_sec = round(avg_queue_len * 45 + random.uniform(-10, 15), 1)

                qd = QueueData(
                    store_id=store.id,
                    counter_id=random.randint(1, active_counters),
                    timestamp=current_time,
                    queue_length=avg_queue_len,
                    avg_wait_time_sec=wait_sec,
                    active_counters=active_counters
                )
                queue_records.append(qd)

            current_time += timedelta(hours=1)

        db.bulk_save_objects(footfall_records)
        db.bulk_save_objects(queue_records)
        db.commit()

        # 6. Generate Recommendations
        recs = [
            Recommendation(
                store_id=store.id,
                category="Cashier",
                title="Open 3 Additional Billing Counters",
                description="Footfall peak predicted between 5 PM - 7 PM. Opening counters 5, 6, and 7 will reduce queue wait times by 42%.",
                priority="HIGH",
                action_taken=False
            ),
            Recommendation(
                store_id=store.id,
                category="Staff",
                title="Shift 2 Sales Staff to Grocery Section",
                description="High customer crowding detected in Produce aisle. Reallocate staff from Electronics.",
                priority="MEDIUM",
                action_taken=True
            ),
            Recommendation(
                store_id=store.id,
                category="Break",
                title="Stagger Evening Cashier Breaks",
                description="Reschedule 6 PM cashier breaks to 4:15 PM to ensure 100% cashier coverage during peak evening rush.",
                priority="HIGH",
                action_taken=False
            )
        ]
        db.add_all(recs)
        db.commit()

        print("Database successfully seeded!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

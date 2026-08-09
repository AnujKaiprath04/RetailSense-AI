from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    sqft = Column(Integer, default=15000)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="store")
    departments = relationship("Department", back_populates="store")
    employees = relationship("Employee", back_populates="store")
    footfall_records = relationship("FootfallData", back_populates="store")
    queue_records = relationship("QueueData", back_populates="store")
    recommendations = relationship("Recommendation", back_populates="store")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="Manager")  # Admin, Manager, Employee
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="users")
    ai_logs = relationship("AILog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Grocery, Electronics, Apparel, Checkout, Security
    target_staff = Column(Integer, default=5)

    store = relationship("Store", back_populates="departments")
    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # Cashier, Sales Associate, Security, Inventory Manager
    hourly_rate = Column(Float, default=18.5)
    status = Column(String(20), default="Active")

    store = relationship("Store", back_populates="employees")
    department = relationship("Department", back_populates="employees")
    shifts = relationship("Shift", back_populates="employee")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    role = Column(String(50), nullable=False)
    status = Column(String(20), default="Scheduled")  # Scheduled, Completed, Absent

    employee = relationship("Employee", back_populates="shifts")


class FootfallData(Base):
    __tablename__ = "footfall_data"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    count = Column(Integer, nullable=False)
    temperature = Column(Float, default=22.0)
    rain_mm = Column(Float, default=0.0)
    is_holiday = Column(Boolean, default=False)
    promotion_active = Column(Boolean, default=False)
    hour = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)

    store = relationship("Store", back_populates="footfall_records")


class QueueData(Base):
    __tablename__ = "queue_data"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    counter_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    queue_length = Column(Integer, nullable=False)
    avg_wait_time_sec = Column(Float, nullable=False)
    active_counters = Column(Integer, default=4)

    store = relationship("Store", back_populates="queue_records")


class CameraEvent(Base):
    __tablename__ = "camera_events"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    camera_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50), nullable=False)  # entry, exit, queue_spike, zone_crowding
    count = Column(Integer, default=1)
    metadata_json = Column(JSON, nullable=True)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    target_timestamp = Column(DateTime, index=True, nullable=False)
    model_name = Column(String(50), nullable=False)  # XGBoost, LightGBM, Prophet, LSTM
    predicted_footfall = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50), nullable=False)  # Cashier, Staff, Inventory, Break
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    action_taken = Column(Boolean, default=False)

    store = relationship("Store", back_populates="recommendations")


class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    target_table = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

# backend/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mediconnect_user:mediconnect_secure_password_2025@localhost:5435/mediconnect")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mediconnect.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class PatientConsultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(String, unique=True, index=True)
    patient_age = Column(Integer, nullable=True)
    patient_gender = Column(String, nullable=True)
    symptoms = Column(Text)
    language = Column(String, default="english")
    diagnosis = Column(Text, nullable=True)
    primary_diagnosis = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    urgency_level = Column(String, nullable=True)
    recommendations = Column(JSON, nullable=True)
    clinic_id = Column(String, nullable=True)
    health_worker_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active, completed, abandoned

class MedicalImage(Base):
    __tablename__ = "medical_images"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(String, index=True)
    image_type = Column(String)  # xray, ultrasound, skin, wound
    image_filename = Column(String)
    analysis_result = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIQuestion(Base):
    __tablename__ = "ai_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(String, index=True)
    question_text = Column(Text)
    question_language = Column(String)
    user_response = Column(Text, nullable=True)
    question_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_consultations = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    total_diagnoses = Column(Integer, default=0)
    languages_used = Column(JSON, default={})
    avg_consultation_time = Column(Float, nullable=True)
    diagnostic_accuracy = Column(Float, nullable=True)

class HealthWorker(Base):
    __tablename__ = "health_workers"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String, unique=True, index=True)
    name = Column(String)
    clinic_name = Column(String)
    location = Column(String)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    training_level = Column(String)  # basic, intermediate, advanced
    languages_spoken = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database operations
class DatabaseOperations:
    def __init__(self):
        self.db = SessionLocal()
    
    def save_consultation(self, consultation_data):
        """Save or update consultation in database"""
        try:
            # Check if consultation already exists
            existing = self.db.query(PatientConsultation).filter(
                PatientConsultation.consultation_id == consultation_data["consultation_id"]
            ).first()
            
            if existing:
                # Update existing consultation
                for key, value in consultation_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                if consultation_data.get("status") == "completed":
                    existing.completed_at = datetime.utcnow()
            else:
                # Create new consultation
                consultation = PatientConsultation(
                    consultation_id=consultation_data["consultation_id"],
                    symptoms=consultation_data.get("symptoms", ""),
                    language=consultation_data.get("language", "english"),
                    diagnosis=consultation_data.get("diagnosis"),
                    primary_diagnosis=consultation_data.get("primary_diagnosis"),
                    confidence_score=consultation_data.get("confidence_score"),
                    urgency_level=consultation_data.get("urgency_level"),
                    recommendations=consultation_data.get("recommendations"),
                    status=consultation_data.get("status", "active")
                )
                self.db.add(consultation)
            
            self.db.commit()
            return existing if existing else consultation
            
        except Exception as e:
            self.db.rollback()
            print(f"Database error in save_consultation: {e}")
            raise e
    
    def save_ai_question(self, consultation_id, question_text, language, order):
        """Save AI question to database"""
        try:
            # Check if question already exists
            existing = self.db.query(AIQuestion).filter(
                AIQuestion.consultation_id == consultation_id,
                AIQuestion.question_order == order
            ).first()
            
            if not existing:
                question = AIQuestion(
                    consultation_id=consultation_id,
                    question_text=question_text,
                    question_language=language,
                    question_order=order
                )
                self.db.add(question)
                self.db.commit()
                return question
            return existing
            
        except Exception as e:
            self.db.rollback()
            print(f"Database error in save_ai_question: {e}")
            return None
    
    def get_consultation_stats(self):
        """Get real-time consultation statistics"""
        try:
            total_consultations = self.db.query(PatientConsultation).count()
            completed_consultations = self.db.query(PatientConsultation).filter(
                PatientConsultation.status == "completed"
            ).count()
            total_questions = self.db.query(AIQuestion).count()
            
            # Calculate average confidence
            avg_confidence = self.db.query(PatientConsultation.confidence_score).filter(
                PatientConsultation.confidence_score.isnot(None)
            ).all()
            
            if avg_confidence:
                avg_conf = sum([c[0] for c in avg_confidence if c[0] is not None]) / len(avg_confidence)
            else:
                avg_conf = 0
            
            return {
                "total_consultations": total_consultations,
                "completed_consultations": completed_consultations,
                "total_questions": total_questions,
                "average_confidence": round(avg_conf * 100, 1) if avg_conf else 0,
                "completion_rate": round((completed_consultations / total_consultations * 100), 1) if total_consultations > 0 else 0
            }
        except Exception as e:
            print(f"Database error in get_consultation_stats: {e}")
            return {
                "total_consultations": 0,
                "completed_consultations": 0,
                "total_questions": 0,
                "average_confidence": 0,
                "completion_rate": 0
            }
    
    def get_language_usage(self):
        """Get language usage statistics"""
        from sqlalchemy import func
        language_stats = self.db.query(
            PatientConsultation.language,
            func.count(PatientConsultation.id)
        ).group_by(PatientConsultation.language).all()
        
        return {lang: count for lang, count in language_stats}
    
    def close(self):
        self.db.close()

# Initialize database
def init_database():
    """Initialize database with tables"""
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
# backend/view_database_sqlalchemy.py
from models.database import SessionLocal, PatientConsultation, AIQuestion, MedicalImage, SystemMetrics
from sqlalchemy import inspect, func
import json
from datetime import datetime

def show_table_schemas():
    """Show all table structures using SQLAlchemy"""
    print("=" * 60)
    print("DATABASE SCHEMA (SQLAlchemy)")
    print("=" * 60)
    
    # Get database inspector
    from models.database import engine
    inspector = inspect(engine)
    
    # Show all tables
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    print()
    
    # Show each table structure
    for table_name in tables:
        print(f"Table: {table_name}")
        print("-" * 40)
        columns = inspector.get_columns(table_name)
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col['default'] else ""
            print(f"  {col['name']:<20} | {str(col['type']):<15} | {nullable:<8} | {default}")
        print()

def show_consultations_data():
    """Show consultations data using SQLAlchemy"""
    print("=" * 60)
    print("CONSULTATIONS DATA")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        consultations = db.query(PatientConsultation).all()
        
        if not consultations:
            print("No consultations found.")
            return
        
        for i, c in enumerate(consultations, 1):
            print(f"Consultation #{i}")
            print("-" * 30)
            print(f"ID: {c.consultation_id}")
            print(f"Language: {c.language}")
            print(f"Patient Age: {c.patient_age}")
            print(f"Patient Gender: {c.patient_gender}")
            print(f"Symptoms: {c.symptoms[:100]}..." if c.symptoms and len(c.symptoms) > 100 else f"Symptoms: {c.symptoms}")
            print(f"Primary Diagnosis: {c.primary_diagnosis}")
            print(f"Confidence Score: {c.confidence_score * 100 if c.confidence_score else 0:.1f}%")
            print(f"Urgency Level: {c.urgency_level}")
            print(f"Status: {c.status}")
            print(f"Created At: {c.created_at}")
            print(f"Completed At: {c.completed_at}")
            
            if c.recommendations:
                print(f"Recommendations: {c.recommendations}")
            print()
            
    finally:
        db.close()

def show_ai_questions_data():
    """Show AI questions data using SQLAlchemy"""
    print("=" * 60)
    print("AI QUESTIONS DATA")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        questions = db.query(AIQuestion).order_by(AIQuestion.consultation_id, AIQuestion.question_order).all()
        
        if not questions:
            print("No AI questions found.")
            return
        
        current_consultation = None
        for q in questions:
            if q.consultation_id != current_consultation:
                current_consultation = q.consultation_id
                print(f"\nConsultation ID: {current_consultation}")
                print("-" * 50)
            
            print(f"  Question #{q.question_order}: {q.question_text}")
            print(f"  Language: {q.question_language}")
            print(f"  User Response: {q.user_response or 'Not answered yet'}")
            print(f"  Asked At: {q.created_at}")
            print()
            
    finally:
        db.close()

def show_statistics():
    """Show database statistics using SQLAlchemy"""
    print("=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Count totals
        total_consultations = db.query(PatientConsultation).count()
        completed_consultations = db.query(PatientConsultation).filter(
            PatientConsultation.status == 'completed'
        ).count()
        total_questions = db.query(AIQuestion).count()
        
        print(f"Total Consultations: {total_consultations}")
        print(f"Completed Consultations: {completed_consultations}")
        print(f"Total AI Questions: {total_questions}")
        print()
        
        # Language breakdown
        print("Language Usage:")
        language_stats = db.query(
            PatientConsultation.language,
            func.count(PatientConsultation.id).label('count')
        ).group_by(PatientConsultation.language).all()
        
        for lang, count in language_stats:
            print(f"  {lang.capitalize()}: {count} consultations")
        print()
        
        # Confidence scores
        print("Confidence Scores:")
        confidence_data = db.query(
            PatientConsultation.primary_diagnosis,
            PatientConsultation.confidence_score
        ).filter(
            PatientConsultation.confidence_score.isnot(None)
        ).all()
        
        if confidence_data:
            for diagnosis, confidence in confidence_data:
                print(f"  {diagnosis}: {confidence * 100:.1f}%")
            
            avg_confidence = sum(c[1] for c in confidence_data) / len(confidence_data)
            print(f"\nAverage Confidence: {avg_confidence * 100:.1f}%")
        else:
            print("  No confidence data available")
        print()
        
        # Urgency levels
        print("Urgency Levels:")
        urgency_stats = db.query(
            PatientConsultation.urgency_level,
            func.count(PatientConsultation.id).label('count')
        ).filter(
            PatientConsultation.urgency_level.isnot(None)
        ).group_by(PatientConsultation.urgency_level).all()
        
        for urgency, count in urgency_stats:
            print(f"  {urgency}: {count} cases")
            
    finally:
        db.close()

def interactive_query():
    """Interactive SQLAlchemy query interface"""
    print("=" * 60)
    print("INTERACTIVE QUERY MODE")
    print("=" * 60)
    print("Available commands:")
    print("1. Show latest consultation")
    print("2. Show consultations by language")
    print("3. Show high confidence diagnoses")
    print("4. Show urgent cases")
    print("5. Exit")
    
    db = SessionLocal()
    try:
        while True:
            choice = input("\nEnter command (1-5): ").strip()
            
            if choice == "1":
                latest = db.query(PatientConsultation).order_by(
                    PatientConsultation.created_at.desc()
                ).first()
                if latest:
                    print(f"Latest consultation: {latest.primary_diagnosis} ({latest.confidence_score * 100:.1f}% confidence)")
                else:
                    print("No consultations found")
                    
            elif choice == "2":
                lang = input("Enter language (english/hausa/yoruba/igbo): ").lower()
                consultations = db.query(PatientConsultation).filter(
                    PatientConsultation.language == lang
                ).all()
                print(f"Found {len(consultations)} consultations in {lang}")
                for c in consultations:
                    print(f"  - {c.primary_diagnosis} ({c.confidence_score * 100 if c.confidence_score else 0:.1f}%)")
                    
            elif choice == "3":
                high_confidence = db.query(PatientConsultation).filter(
                    PatientConsultation.confidence_score >= 0.8
                ).all()
                print(f"High confidence diagnoses (>=80%):")
                for c in high_confidence:
                    print(f"  - {c.primary_diagnosis}: {c.confidence_score * 100:.1f}%")
                    
            elif choice == "4":
                urgent = db.query(PatientConsultation).filter(
                    PatientConsultation.urgency_level.in_(['HIGH', 'CRITICAL'])
                ).all()
                print(f"Urgent cases:")
                for c in urgent:
                    print(f"  - {c.primary_diagnosis} ({c.urgency_level})")
                    
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please enter 1-5.")
                
    finally:
        db.close()

def main():
    """Main function to display all database information"""
    print("MediConnect AI Database Viewer (SQLAlchemy)")
    print("=" * 60)
    
    show_table_schemas()
    show_consultations_data()
    show_ai_questions_data()
    show_statistics()
    
    # Ask if user wants interactive mode
    response = input("Do you want to enter interactive query mode? (y/n): ").lower()
    if response in ['y', 'yes']:
        interactive_query()

if __name__ == "__main__":
    main()
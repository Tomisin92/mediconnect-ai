from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import openai
import json
import os
from typing import Dict, List
from pydantic import BaseModel
from dotenv import load_dotenv
from models.database import DatabaseOperations, get_db, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
import re

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="MediConnect AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client - API key from environment only
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable not set")
    print("Please set it with one of these methods:")
    print("1. Create .env file with: OPENAI_API_KEY=your_key_here")
    print("2. Set environment variable: set OPENAI_API_KEY=your_key_here")
else:
    print(f"OpenAI API Key loaded successfully: {OPENAI_API_KEY[:8]}...")

# Create OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Initialize database operations
db_ops = DatabaseOperations()

# Conversation tracking (in-memory for active sessions)
conversations = {}

class ConsultationRequest(BaseModel):
    consultation_id: str
    user_input: str
    language: str = "english"
    has_image: bool = False
    image_description: str = ""

def extract_patient_information(conversation_history: List) -> Dict:
    """Extract patient information from conversation history"""
    patient_info = {
        'all_symptoms': [],
        'age': None,
        'gender': None,
        'duration': None,
        'severity': None,
        'fever_status': None,
        'medications': None,
        'full_conversation': ""
    }
    
    # Combine all conversation text
    for turn in conversation_history:
        if 'user' in turn:
            patient_info['full_conversation'] += f"Patient info: {turn['user']} "
    
    print(f"DEBUG - Full conversation for OpenAI: {patient_info['full_conversation']}")
    return patient_info

async def get_openai_medical_diagnosis(patient_info: Dict, language: str) -> Dict:
    """Use OpenAI GPT-4 to generate professional medical diagnosis"""
    
    if not client:
        raise Exception("OpenAI API not available")
    
    # Create comprehensive medical prompt
    medical_prompt = f"""
You are a senior medical doctor providing a professional medical consultation. Based on the patient information provided, give an accurate medical diagnosis with specific treatment recommendations.

PATIENT INFORMATION:
{patient_info['full_conversation']}

IMPORTANT INSTRUCTIONS:
1. Analyze the symptoms carefully and provide the most likely primary diagnosis
2. Consider the patient's age and symptom presentation
3. If no fever is mentioned or explicitly stated "no fever", DO NOT diagnose fever-related conditions
4. For diarrhea + vomiting without fever, consider gastroenteritis, food poisoning, or non-infectious causes
5. Provide specific, actionable medical recommendations with exact dosages
6. Consider Nigerian medical context (availability of medications, common conditions)
7. Respond in {language} language
8. Be specific and professional - this is for a medical competition

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "primary_diagnosis": "Specific medical diagnosis based on symptoms presented",
    "confidence": 0.85,
    "urgency": "LOW/MODERATE/HIGH/CRITICAL",
    "recommendations": [
        "Specific recommendation 1 with dosages if applicable",
        "Specific recommendation 2 with clear instructions",
        "Specific recommendation 3 with monitoring guidelines",
        "Specific recommendation 4 with follow-up criteria",
        "Specific recommendation 5 with patient education"
    ],
    "clinical_reasoning": "Brief explanation of why this diagnosis fits the presentation"
}}

EXAMPLES OF GOOD DIAGNOSES:
- For diarrhea + vomiting without fever: "Acute gastroenteritis (likely viral or dietary indiscretion)"
- For neck pain without fever: "Cervical strain with muscle spasm"
- For fever + headache: "Viral syndrome, rule out malaria"

CRITICAL: Base diagnosis ONLY on symptoms actually present. Do not add symptoms not mentioned.
"""

    try:
        print(f"DEBUG - Sending diagnosis request to OpenAI GPT-4")
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a specialist medical doctor. Provide accurate medical diagnoses in {language} language. Focus on the exact symptoms presented. This is for a medical competition so accuracy is critical."
                },
                {
                    "role": "user", 
                    "content": medical_prompt
                }
            ],
            temperature=0.3,  # Low temperature for consistent medical responses
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        print(f"DEBUG - OpenAI diagnosis response: {ai_response}")
        
        # Parse JSON response
        try:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                diagnosis_data = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['primary_diagnosis', 'confidence', 'urgency', 'recommendations']
                if all(field in diagnosis_data for field in required_fields):
                    print(f"DEBUG - Successfully parsed OpenAI diagnosis: {diagnosis_data['primary_diagnosis']}")
                    return diagnosis_data
                else:
                    raise ValueError("Missing required fields in OpenAI response")
                    
        except (json.JSONDecodeError, ValueError) as e:
            print(f"DEBUG - JSON parsing failed: {e}")
            # Try to extract key information from text response
            return extract_diagnosis_from_text(ai_response, language)
            
    except Exception as e:
        print(f"DEBUG - OpenAI API error: {e}")
        raise e

def extract_diagnosis_from_text(ai_text: str, language: str) -> Dict:
    """Extract diagnosis information from text when JSON parsing fails"""
    
    # Look for diagnosis in the text
    diagnosis_keywords = ['diagnosis', 'condition', 'likely', 'probably', 'appears to be']
    primary_diagnosis = "Clinical assessment based on symptoms presented"
    
    lines = ai_text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in diagnosis_keywords):
            # Clean up the line to extract diagnosis
            diagnosis_text = line.strip('*').strip('-').strip()
            if len(diagnosis_text) > 10:  # Reasonable diagnosis length
                primary_diagnosis = diagnosis_text
                break
    
    return {
        "primary_diagnosis": primary_diagnosis,
        "confidence": 0.75,
        "urgency": "MODERATE", 
        "recommendations": [
            "Follow symptomatic treatment as clinically indicated",
            "Monitor patient response to initial interventions",
            "Maintain adequate hydration and nutrition",
            "Return for follow-up if symptoms persist or worsen",
            "Seek immediate care if severe symptoms develop"
        ],
        "clinical_reasoning": "Diagnosis extracted from clinical assessment text"
    }

async def get_openai_questions(patient_info: Dict, conversation_history: List, language: str) -> Dict:
    """Use OpenAI to generate intelligent follow-up questions"""
    
    if not client:
        raise Exception("OpenAI API not available")
    
    conversation_context = "\n".join([
        f"Health Worker: {turn['user']}\nAI Doctor: {turn['ai']}" 
        for turn in conversation_history
    ])
    
    question_prompt = f"""
You are an expert medical doctor conducting a patient consultation. Based on the conversation so far, ask 2-3 intelligent medical questions to gather essential information for accurate diagnosis.

CONVERSATION SO FAR:
{conversation_context}

LATEST PATIENT INFORMATION: 
{patient_info['full_conversation']}

INSTRUCTIONS:
1. Ask specific medical questions that will help with diagnosis
2. Don't repeat questions already asked
3. Focus on key missing information (age, duration, severity, associated symptoms)
4. Ask questions in {language} language
5. Be concise and professional

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "questions": [
        "Medical question 1 in {language}",
        "Medical question 2 in {language}"
    ],
    "ai_response": "Brief professional response in {language} explaining why you need this information"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a medical doctor asking diagnostic questions in {language}. Be professional and focused."
                },
                {
                    "role": "user",
                    "content": question_prompt
                }
            ],
            temperature=0.4,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        print(f"DEBUG - OpenAI questions response: {ai_response}")
        
        # Parse JSON response
        try:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                questions_data = json.loads(json_str)
                return questions_data
        except:
            pass
    except Exception as e:
        print(f"DEBUG - OpenAI questions error: {e}")
    
    # Fallback questions if OpenAI fails
    fallback_questions = {
        "english": {
            "questions": ["What is the patient's age?", "How long have these symptoms been present?"],
            "ai_response": "I need some additional information to provide an accurate diagnosis."
        },
        "hausa": {
            "questions": ["Menene shekarun majinyaci?", "Har yaushe waɗannan alamun suka kasance?"],
            "ai_response": "Ina bukatar ƙarin bayani don ba da ingantaccen ganewar asali."
        },
        "yoruba": {
            "questions": ["Elo ni ọjọ ori alaisan?", "Elo ni awon ami aisan yi ti wa?"],
            "ai_response": "Mo nilo alaye diẹ sii lati fun ni iwadii to peye."
        },
        "igbo": {
            "questions": ["Gịnị bụ afọ onye ọrịa?", "Ogologo oge ole ka ihe mgbaàmà ndị a nọrọla?"],
            "ai_response": "Achọrọ m obere ozi iji nye nchọpụta ziri ezi."
        }
    }
    
    return fallback_questions.get(language, fallback_questions["english"])

async def analyze_with_openai_medical_ai(consultation_id: str, user_input: str, language: str, conversation_history: List = None, has_image: bool = False, image_description: str = "") -> Dict:
    """OpenAI-powered medical consultation with intelligent diagnosis"""
    
    if conversation_history is None:
        conversation_history = []
    
    # Count exchanges
    exchange_count = len(conversation_history)
    
    print(f"DEBUG - Exchange count: {exchange_count}")
    print(f"DEBUG - Current user input: {user_input}")
    
    # Extract patient information
    patient_info = extract_patient_information(conversation_history + [{'user': user_input}])
    
    # Add image information if present
    if has_image and image_description:
        patient_info['full_conversation'] += f" [MEDICAL IMAGE: {image_description}]"
    
    # Determine if we should provide diagnosis or ask more questions
    # Force diagnosis after 2-3 exchanges or if we have sufficient information
    should_diagnose = (
        exchange_count >= 2 or
        (exchange_count >= 1 and len(patient_info['full_conversation'].split()) > 10)
    )
    
    print(f"DEBUG - Should diagnose: {should_diagnose}")
    
    if should_diagnose:
        # Use OpenAI for final diagnosis
        try:
            diagnosis = await get_openai_medical_diagnosis(patient_info, language)
            
            response_texts = {
                'english': "Based on the clinical presentation and symptoms described, here is my professional medical assessment:",
                'hausa': "Bisa ga alamun da tarihin likitanci da aka bayar, ga kimantata na kwararre:",
                'yoruba': "Ni ibamu lori iṣafihan ati itan ilera ti a fun, eyi ni iṣiro mi ti ogbọn:",
                'igbo': "Dabere na ngosipụta ahụike na akụkọ enyere, nke a bụ nyocha ahụike m nke ọkachamara:"
            }
            
            return {
                "type": "diagnosis",
                "questions": [],
                "ai_response": response_texts.get(language, response_texts['english']),
                "diagnosis": diagnosis,
                "reasoning": f"OpenAI GPT-4 medical diagnosis after {exchange_count + 1} exchanges",
                "ready_for_diagnosis": True
            }
            
        except Exception as e:
            print(f"DEBUG - OpenAI diagnosis failed: {e}")
            # If OpenAI fails, provide a basic response but indicate the limitation
            return {
                "type": "diagnosis",
                "questions": [],
                "ai_response": "Based on available information, here is a preliminary assessment:",
                "diagnosis": {
                    "primary_diagnosis": "Medical consultation required - OpenAI diagnosis unavailable",
                    "confidence": 0.60,
                    "urgency": "MODERATE",
                    "recommendations": [
                        "Comprehensive clinical examination recommended",
                        "Basic supportive care as clinically indicated",
                        "Monitor symptoms and vital signs",
                        "Follow-up if symptoms persist or worsen",
                        "Consider specialist referral if complex presentation"
                    ],
                    "clinical_reasoning": "Limited assessment due to system limitations"
                },
                "reasoning": "Fallback response - OpenAI unavailable",
                "ready_for_diagnosis": True
            }
    
    else:
        # Use OpenAI for intelligent questions
        try:
            questions_response = await get_openai_questions(patient_info, conversation_history, language)
            
            return {
                "type": "questions",
                "questions": questions_response["questions"],
                "ai_response": questions_response["ai_response"],
                "diagnosis": None,
                "reasoning": f"OpenAI-generated follow-up questions (exchange {exchange_count + 1})",
                "ready_for_diagnosis": False
            }
            
        except Exception as e:
            print(f"DEBUG - OpenAI questions failed: {e}")
            # Fallback questions
            fallback = await get_openai_questions({}, [], language)
            return {
                "type": "questions",
                "questions": fallback["questions"],
                "ai_response": fallback["ai_response"],
                "diagnosis": None,
                "reasoning": f"Fallback questions (exchange {exchange_count + 1})",
                "ready_for_diagnosis": False
            }

@app.get("/")
async def root():
    return {"message": "MediConnect AI OpenAI-Powered Medical Consultation API is running!", "status": "healthy"}

@app.post("/start_consultation")
async def start_consultation(language: str = "english"):
    """Start a new OpenAI-powered medical consultation"""
    import uuid
    consultation_id = str(uuid.uuid4())
    
    # Initialize conversation in memory
    conversations[consultation_id] = {
        "history": [],
        "language": language,
        "stage": "initial",
        "created_at": datetime.utcnow()
    }
    
    # Save to database
    try:
        db_ops.save_consultation({
            "consultation_id": consultation_id,
            "symptoms": "",
            "language": language,
            "status": "active"
        })
    except Exception as e:
        print(f"Database save error: {e}")
    
    initial_prompt = {
        "english": "Hello! I'm Dr. MediConnect AI, powered by advanced medical AI. Please describe the patient's symptoms and I'll provide a comprehensive diagnosis.",
        "hausa": "Sannu! Ni ne Dokta MediConnect AI, wanda ke da ƙarfin ilimin AI na likitanci. Don Allah ka bayyana alamun majinyaci zan ba da cikakkiyar ganewar asali.",
        "yoruba": "Bawo! Emi ni Dokita MediConnect AI, ti o ni agbara AI ilera to ga. Jọwọ ṣapejuwe awon ami aisan alaisan, emi yoo fun yin ni iwadii pipe.",
        "igbo": "Ndewo! Abụ m Dọkịta MediConnect AI, nke nwere ike AI ahụike dị elu. Biko kọwaa ihe mgbaàmà onye ọrịa, m ga-enye gị nchọpụta zuru ezu."
    }
    
    initial_questions = {
        "english": [
            "What symptoms is the patient experiencing?",
            "When did these symptoms start?", 
            "How severe are the symptoms?"
        ],
        "hausa": [
            "Wane alamomi majinyaci yake fuskanta?",
            "Yaushe waɗannan alamun suka fara?",
            "Yaya tsananin alamun?"
        ],
        "yoruba": [
            "Awon ami aisan wo ni alaisan n ni?",
            "Nigbati wo ni awon ami aisan bẹrẹ?",
            "Bawo ni awon ami aisan ṣe le to?"
        ],
        "igbo": [
            "Kedu ihe mgbaàmà onye ọrịa na-enwe?",
            "Oleizi ka ihe mgbaàmà ndị a malitere?",
            "Kedu ka ihe mgbaàmà ndị ahụ si sie ike?"
        ]
    }
    
    return {
        "consultation_id": consultation_id,
        "ai_response": initial_prompt.get(language, initial_prompt["english"]),
        "questions": initial_questions.get(language, initial_questions["english"]),
        "status": "consultation_started"
    }

@app.post("/continue_consultation")
async def continue_consultation(request: ConsultationRequest):
    """Continue an ongoing OpenAI-powered medical consultation"""
    
    consultation_id = request.consultation_id
    user_input = request.user_input
    language = request.language
    has_image = request.has_image
    image_description = request.image_description
    
    # Get conversation history
    if consultation_id not in conversations:
        return {"error": "Consultation not found. Please start a new consultation."}
    
    conversation_history = conversations[consultation_id]["history"]
    
    # Get OpenAI-powered response
    analysis = await analyze_with_openai_medical_ai(
        consultation_id, 
        user_input, 
        language, 
        conversation_history,
        has_image,
        image_description
    )
    
    # Update conversation history
    conversations[consultation_id]["history"].append({
        "user": user_input,
        "ai": analysis["ai_response"],
        "has_image": has_image
    })
    
    # Save AI questions to database
    if analysis["type"] == "questions":
        try:
            for i, question in enumerate(analysis["questions"]):
                db_ops.save_ai_question(
                    consultation_id, 
                    question, 
                    language, 
                    i + 1
                )
        except Exception as e:
            print(f"Database save error: {e}")
    
    # Return response based on type
    if analysis["type"] == "questions":
        return {
            "type": "questions",
            "ai_response": analysis["ai_response"],
            "questions": analysis["questions"],
            "reasoning": analysis["reasoning"],
            "ready_for_diagnosis": analysis["ready_for_diagnosis"],
            "consultation_continues": True
        }
    else:
        # OpenAI diagnosis ready - save to database
        try:
            db_ops.save_consultation({
                "consultation_id": consultation_id,
                "symptoms": user_input,
                "language": language,
                "diagnosis": analysis["ai_response"],
                "primary_diagnosis": analysis["diagnosis"]["primary_diagnosis"],
                "confidence_score": analysis["diagnosis"]["confidence"],
                "urgency_level": analysis["diagnosis"]["urgency"],
                "recommendations": analysis["diagnosis"]["recommendations"],
                "status": "completed"
            })
        except Exception as e:
            print(f"Database save error: {e}")
            
        return {
            "type": "diagnosis",
            "ai_response": analysis["ai_response"],
            "diagnosis": analysis["diagnosis"],
            "reasoning": analysis["reasoning"],
            "consultation_complete": True,
            "consultation_id": consultation_id
        }

@app.get("/health")
async def health_check():
    return {
        "status": "MediConnect AI OpenAI Medical Consultation ready!",
        "ai_enabled": bool(OPENAI_API_KEY),
        "model": "gpt-4",
        "features": [
            "openai_powered_diagnosis", 
            "intelligent_medical_questioning", 
            "competition_ready", 
            "contextual_accuracy",
            "multilingual_medical_ai"
        ],
        "api_key_configured": bool(OPENAI_API_KEY),
        "database_connected": True,
        "diagnostic_engine": "OpenAI GPT-4 Medical Intelligence"
    }

@app.get("/stats")
async def get_system_stats():
    """Get real-time system statistics from database"""
    try:
        stats = db_ops.get_consultation_stats()
        language_usage = db_ops.get_language_usage()
        
        return {
            "total_consultations": stats["total_consultations"],
            "completed_consultations": stats["completed_consultations"],
            "total_questions": stats["total_questions"],
            "average_confidence": stats["average_confidence"],
            "completion_rate": stats["completion_rate"],
            "language_usage": language_usage,
            "database_status": "connected",
            "ai_engine": "OpenAI GPT-4 Powered",
            "competition_ready": True
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {
            "total_consultations": 0,
            "completed_consultations": 0,
            "total_questions": 0,
            "average_confidence": 0,
            "completion_rate": 0,
            "language_usage": {},
            "database_status": "error",
            "error_message": str(e)
        }

# Database initialization
from models.database import create_tables

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        create_tables()
        print("Database tables created successfully!")
        print("OpenAI GPT-4 Powered Medical AI System Ready!")
    except Exception as e:
        print(f"Database table creation error: {e}")

if __name__ == "__main__":
    # Initialize database tables
    create_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)

# # from fastapi import FastAPI, UploadFile, File
# # from fastapi.middleware.cors import CORSMiddleware
# # import uvicorn
# # import openai
# # import json
# # import os
# # from typing import Dict, List
# # from pydantic import BaseModel
# # from dotenv import load_dotenv

# # # Load environment variables from .env file
# # load_dotenv()

# # app = FastAPI(title="MediConnect AI API", version="1.0.0")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # Initialize OpenAI client - API key from environment only
# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # if not OPENAI_API_KEY:
# #     print("WARNING: OPENAI_API_KEY environment variable not set")
# #     print("Please set it with one of these methods:")
# #     print("1. Create .env file with: OPENAI_API_KEY=your_key_here")
# #     print("2. Set environment variable: set OPENAI_API_KEY=your_key_here")
# # else:
# #     print(f"OpenAI API Key loaded successfully: {OPENAI_API_KEY[:8]}...")

# # # Create OpenAI client
# # client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# # # Conversation tracking
# # conversations = {}

# # class ConsultationRequest(BaseModel):
# #     consultation_id: str
# #     user_input: str
# #     language: str = "english"

# # async def analyze_with_interactive_ai(consultation_id: str, user_input: str, language: str, conversation_history: List = None) -> Dict:
# #     """Interactive medical consultation with AI asking follow-up questions"""
    
# #     if conversation_history is None:
# #         conversation_history = []
    
# #     # Build conversation context
# #     conversation_context = "\n".join([
# #         f"Health Worker: {turn['user']}\nAI: {turn['ai']}" 
# #         for turn in conversation_history
# #     ])
    
# #     prompt = f"""
# #     You are an expert medical AI assistant for rural Nigerian healthcare workers. You conduct interactive medical consultations by asking intelligent follow-up questions.

# #     CONSULTATION CONTEXT:
# #     Language: {language} - IMPORTANT: Respond in {language} language for questions and responses
# #     Previous conversation:
# #     {conversation_context}
    
# #     Current input: {user_input}
    
# #     Your role is to:
# #     1. If initial symptoms are clear and concerning, provide immediate diagnosis with 1-2 follow-up questions
# #     2. Only ask 1-2 critical questions maximum before making a diagnosis
# #     3. Prioritize speed and actionable decisions for rural healthcare settings
# #     4. Always consider Nigerian medical context (malaria, tropical diseases, resource constraints)
# #     5. Be decisive - rural health workers need quick, confident guidance
# #     6. CRITICAL: Ask questions in {language} language, not English
    
# #     LANGUAGE GUIDELINES:
# #     - If language is "yoruba": Ask questions in Yoruba
# #     - If language is "hausa": Ask questions in Hausa  
# #     - If language is "igbo": Ask questions in Igbo
# #     - If language is "english": Ask questions in English
    
# #     DECISION CRITERIA:
# #     - Fever + any concerning symptoms = Immediate diagnosis (likely malaria in Nigeria)
# #     - Clear symptom patterns = Diagnose after 1 question round maximum
# #     - Pregnancy complications = Immediate diagnosis
# #     - Pediatric emergencies = Quick assessment and action
    
# #     Respond in this EXACT JSON format:
# #     {{
# #         "type": "questions" OR "diagnosis",
# #         "questions": [
# #             "Question 1 in {language} language",
# #             "Question 2 in {language} language if needed"
# #         ],
# #         "ai_response": "Brief, decisive response in {language}",
# #         "diagnosis": {{
# #             "primary_diagnosis": "Most likely condition",
# #             "confidence": 0.85,
# #             "recommendations": ["Action 1", "Action 2"],
# #             "urgency": "HIGH/MODERATE/LOW"
# #         }},
# #         "reasoning": "Quick clinical reasoning",
# #         "ready_for_diagnosis": true/false
# #     }}
    
# #     EXAMPLE QUESTIONS BY LANGUAGE:
# #     English: "How long has the fever been present?"
# #     Yoruba: "Bawo ni iba naa ti wa fun elo?"
# #     Hausa: "Har yaushe zazzabi ya kasance?"
# #     Igbo: "Ogologo oge ole ka ahụ ọkụ ahụ nọrịla?"
    
# #     Guidelines:
# #     - MAXIMUM 2 questions before providing diagnosis
# #     - If fever mentioned = likely malaria, ask 1 question then diagnose
# #     - If clear symptoms = diagnose immediately
# #     - Prioritize action over perfect information
# #     - Be confident and decisive like an experienced rural doctor
# #     - ALWAYS ask questions in the specified language: {language}
# #     """
    
# #     try:
# #         if not client:
# #             raise Exception("OpenAI API key not configured")
            
# #         response = client.chat.completions.create(
# #             model="gpt-3.5-turbo",
# #             messages=[
# #                 {
# #                     "role": "system", 
# #                     "content": "You are a medical expert AI conducting interactive consultations for rural Nigerian healthcare. Always respond in the exact JSON format requested."
# #                 },
# #                 {
# #                     "role": "user",
# #                     "content": prompt
# #                 }
# #             ],
# #             temperature=0.3,
# #             max_tokens=1000
# #         )
        
# #         ai_response = response.choices[0].message.content
        
# #         # Parse JSON response
# #         try:
# #             json_start = ai_response.find('{')
# #             json_end = ai_response.rfind('}') + 1
# #             json_str = ai_response[json_start:json_end]
# #             analysis = json.loads(json_str)
            
# #             # Debug: Print what AI actually returned
# #             print(f"DEBUG - Language requested: {language}")
# #             print(f"DEBUG - AI questions returned: {analysis.get('questions', [])}")
            
# #             return analysis
            
# #         except json.JSONDecodeError:
# #             # Fallback structured response
# #             return {
# #                 "type": "questions",
# #                 "questions": [
# #                     "How long has the patient had these symptoms?" if language == "english" else
# #                     "Har yaushe majinyaci ya kasance da waɗannan alamun?" if language == "hausa" else
# #                     "Elo ni alaisan ti ni awon ami aisan wonyi?" if language == "yoruba" else
# #                     "Ogologo oge ole ka onye ọrịa nwere ihe mgbaàmà ndị a?" if language == "igbo" else
# #                     "How long has the patient had these symptoms?",
                    
# #                     "What is the patient's age and gender?" if language == "english" else
# #                     "Menene shekarun majinyaci da jinsinsa?" if language == "hausa" else
# #                     "Elo ni ọjọ ori alaisan ati abo re?" if language == "yoruba" else
# #                     "Gịnị bụ afọ onye ọrịa na okike ya?" if language == "igbo" else
# #                     "What is the patient's age and gender?"
# #                 ],
# #                 "ai_response": "I need to ask a few questions to help with the diagnosis." if language == "english" else
# #                               "Ina bukatar in yi wasu tambayoyi don taimakawa da ganewar asali." if language == "hausa" else
# #                               "Mo nilo lati beere awon ibeere diẹ lati ṣe iranwọ pẹlu iwadii." if language == "yoruba" else
# #                               "Achọrọ m ịjụ ajụjụ ole na ole iji nyere aka na nchọpụta." if language == "igbo" else
# #                               "I need to ask a few questions to help with the diagnosis.",
# #                 "diagnosis": None,
# #                 "reasoning": "Gathering initial information",
# #                 "ready_for_diagnosis": False
# #             }
            
# #     except Exception as e:
# #         print(f"OpenAI API error: {e}")
# #         print(f"Error type: {type(e)}")
# #         print(f"Symptoms received: {user_input}")
        
# #         # More detailed error handling
# #         if "insufficient_quota" in str(e):
# #             error_msg = "OpenAI API quota exceeded - need to add billing"
# #         elif "invalid_api_key" in str(e):
# #             error_msg = "Invalid OpenAI API key"
# #         elif "rate_limit" in str(e):
# #             error_msg = "Rate limit exceeded - too many requests"
# #         else:
# #             error_msg = f"API connection error: {str(e)}"
            
# #         return {
# #             "type": "questions",
# #             "questions": [
# #                 "Can you tell me more about when the symptoms started?" if language == "english" else
# #                 "Za ku iya gaya mani ƙarin game da lokacin da alamun suka fara?" if language == "hausa" else
# #                 "Ṣe o le sọ fun mi diẹ sii nipa igba ti awon ami aisan bẹrẹ?" if language == "yoruba" else
# #                 "Ị nwere ike ịgwa m karịa banyere mgbe ihe mgbaàmà malitere?" if language == "igbo" else
# #                 "Can you tell me more about when the symptoms started?",
                
# #                 "What is the patient's age?" if language == "english" else
# #                 "Menene shekarun majinyaci?" if language == "hausa" else
# #                 "Elo ni ọjọ ori alaisan?" if language == "yoruba" else
# #                 "Gịnị bụ afọ onye ọrịa?" if language == "igbo" else
# #                 "What is the patient's age?"
# #             ],
# #             "ai_response": "I'm here to help with the consultation. Let me ask some questions." if language == "english" else
# #                           "Ina nan don taimaka da shawarwarin. Bari in yi wasu tambayoyi." if language == "hausa" else
# #                           "Mo wa nibi lati ṣe iranwọ pẹlu ibaraenisoro. Jẹ ki n beere awon ibeere." if language == "yoruba" else
# #                           "Anọ m ebe a iji nyere aka na mkparịta ụka. Ka m jụọ ajụjụ ụfọdụ." if language == "igbo" else
# #                           "I'm here to help with the consultation. Let me ask some questions.",
# #             "diagnosis": None,
# #             "reasoning": f"System error - gathering basic information in {language}",
# #             "ready_for_diagnosis": False
# #         }

# # @app.get("/")
# # async def root():
# #     return {"message": "MediConnect AI Interactive Consultation API is running!", "status": "healthy"}

# # @app.post("/start_consultation")
# # async def start_consultation(language: str = "english"):
# #     """Start a new medical consultation"""
# #     import uuid
# #     consultation_id = str(uuid.uuid4())
    
# #     # Initialize conversation
# #     conversations[consultation_id] = {
# #         "history": [],
# #         "language": language,
# #         "stage": "initial"
# #     }
    
# #     initial_prompt = {
# #         "english": "Hello! Tell me the patient's main symptoms and I'll provide a quick diagnosis.",
# #         "hausa": "Sannu! Gaya mani manyan alamun majinyaci zan ba da ganewar cikin sauri.",
# #         "yoruba": "Bawo! So fun mi awon ami aisan pataki alaisan naa, emi yoo fun yin ni iwadii kiakia.",
# #         "igbo": "Ndewo! Gwa m isi ihe mgbaàmà onye ọrịa, m ga-enye gị nchọpụta ngwa ngwa."
# #     }
    
# #     initial_questions = {
# #         "english": [
# #             "What are the main symptoms?",
# #             "When did they start?", 
# #             "How is the patient feeling overall?"
# #         ],
# #         "hausa": [
# #             "Menene manyan alamun?",
# #             "Yaushe suka fara?",
# #             "Yaya majinyaci yake ji gabaɗaya?"
# #         ],
# #         "yoruba": [
# #             "Kini awon ami aisan pataki?",
# #             "Nigbati wo ni won bẹrẹ?",
# #             "Bawo ni alaisan ṣe ni rilara lapapọ?"
# #         ],
# #         "igbo": [
# #             "Gịnị bụ isi ihe mgbaàmà?",
# #             "Oleizi ka ha malitere?",
# #             "Kedu ka onye ọrịa si enwe mmetụta n'ozuzu?"
# #         ]
# #     }
    
# #     return {
# #         "consultation_id": consultation_id,
# #         "ai_response": initial_prompt.get(language, initial_prompt["english"]),
# #         "questions": initial_questions.get(language, initial_questions["english"]),
# #         "status": "consultation_started"
# #     }

# # @app.post("/continue_consultation")
# # async def continue_consultation(request: ConsultationRequest):
# #     """Continue an ongoing medical consultation"""
    
# #     consultation_id = request.consultation_id
# #     user_input = request.user_input
# #     language = request.language
    
# #     # Get conversation history
# #     if consultation_id not in conversations:
# #         return {"error": "Consultation not found. Please start a new consultation."}
    
# #     conversation_history = conversations[consultation_id]["history"]
    
# #     # Get AI response
# #     analysis = await analyze_with_interactive_ai(consultation_id, user_input, language, conversation_history)
    
# #     # Update conversation history
# #     conversations[consultation_id]["history"].append({
# #         "user": user_input,
# #         "ai": analysis["ai_response"]
# #     })
    
# #     # Return response based on type
# #     if analysis["type"] == "questions":
# #         return {
# #             "type": "questions",
# #             "ai_response": analysis["ai_response"],
# #             "questions": analysis["questions"],
# #             "reasoning": analysis["reasoning"],
# #             "ready_for_diagnosis": analysis["ready_for_diagnosis"],
# #             "consultation_continues": True
# #         }
# #     else:
# #         # Diagnosis ready
# #         return {
# #             "type": "diagnosis",
# #             "ai_response": analysis["ai_response"],
# #             "diagnosis": analysis["diagnosis"],
# #             "reasoning": analysis["reasoning"],
# #             "consultation_complete": True,
# #             "consultation_id": consultation_id
# #         }

# # @app.get("/health")
# # async def health_check():
# #     return {
# #         "status": "MediConnect AI Interactive Consultation ready!",
# #         "ai_enabled": bool(OPENAI_API_KEY),
# #         "model": "gpt-3.5-turbo",
# #         "features": ["interactive_consultation", "follow_up_questions", "guided_diagnosis"],
# #         "api_key_configured": bool(OPENAI_API_KEY)
# #     }

# # if __name__ == "__main__":
# #     uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
# import openai
# import json
# import os
# from typing import Dict, List
# from pydantic import BaseModel
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# app = FastAPI(title="MediConnect AI API", version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize OpenAI client - API key from environment only
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# if not OPENAI_API_KEY:
#     print("WARNING: OPENAI_API_KEY environment variable not set")
#     print("Please set it with one of these methods:")
#     print("1. Create .env file with: OPENAI_API_KEY=your_key_here")
#     print("2. Set environment variable: set OPENAI_API_KEY=your_key_here")
# else:
#     print(f"OpenAI API Key loaded successfully: {OPENAI_API_KEY[:8]}...")

# # Create OpenAI client
# client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# # Conversation tracking
# conversations = {}

# class ConsultationRequest(BaseModel):
#     consultation_id: str
#     user_input: str
#     language: str = "english"
#     has_image: bool = False
#     image_description: str = ""

# async def analyze_with_interactive_ai(consultation_id: str, user_input: str, language: str, conversation_history: List = None, has_image: bool = False, image_description: str = "") -> Dict:
#     """Interactive medical consultation with AI asking follow-up questions"""
    
#     if conversation_history is None:
#         conversation_history = []
    
#     # Build conversation context
#     conversation_context = "\n".join([
#         f"Health Worker: {turn['user']}\nAI: {turn['ai']}" 
#         for turn in conversation_history
#     ])
    
#     prompt = f"""
#     You are an expert medical AI assistant for rural Nigerian healthcare workers. You conduct interactive medical consultations by asking intelligent follow-up questions.

#     CONSULTATION CONTEXT:
#     Language: {language} - IMPORTANT: Respond in {language} language for questions and responses
#     Previous conversation:
#     {conversation_context}
    
#     Current input: {user_input}
    
#     {f"MEDICAL IMAGE PROVIDED: {image_description}" if has_image else ""}
#     {f"IMPORTANT: Consider the medical image in your diagnosis and questions" if has_image else ""}
    
#     Your role is to:
#     1. If initial symptoms are clear and concerning, provide immediate diagnosis with 1-2 follow-up questions
#     2. Only ask 1-2 critical questions maximum before making a diagnosis
#     3. Prioritize speed and actionable decisions for rural healthcare settings
#     4. Always consider Nigerian medical context (malaria, tropical diseases, resource constraints)
#     5. Be decisive - rural health workers need quick, confident guidance
#     6. CRITICAL: Ask questions in {language} language, not English
    
#     LANGUAGE GUIDELINES:
#     - If language is "yoruba": Ask questions in Yoruba
#     - If language is "hausa": Ask questions in Hausa  
#     - If language is "igbo": Ask questions in Igbo
#     - If language is "english": Ask questions in English
    
#     DECISION CRITERIA:
#     - Fever + any concerning symptoms = Immediate diagnosis (likely malaria in Nigeria)
#     - Clear symptom patterns = Diagnose after 1 question round maximum
#     - Pregnancy complications = Immediate diagnosis
#     - Pediatric emergencies = Quick assessment and action
    
#     Respond in this EXACT JSON format:
#     {{
#         "type": "questions" OR "diagnosis",
#         "questions": [
#             "Question 1 in {language} language",
#             "Question 2 in {language} language if needed"
#         ],
#         "ai_response": "Brief, decisive response in {language}",
#         "diagnosis": {{
#             "primary_diagnosis": "Most likely condition",
#             "confidence": 0.85,
#             "recommendations": ["Action 1", "Action 2"],
#             "urgency": "HIGH/MODERATE/LOW"
#         }},
#         "reasoning": "Quick clinical reasoning",
#         "ready_for_diagnosis": true/false
#     }}
    
#     EXAMPLE QUESTIONS BY LANGUAGE:
#     English: "How long has the fever been present?"
#     Yoruba: "Bawo ni iba naa ti wa fun elo?"
#     Hausa: "Har yaushe zazzabi ya kasance?"
#     Igbo: "Ogologo oge ole ka ahụ ọkụ ahụ nọrịla?"
    
#     Guidelines:
#     - MAXIMUM 2 questions before providing diagnosis
#     - If fever mentioned = likely malaria, ask 1 question then diagnose
#     - If clear symptoms = diagnose immediately
#     - Prioritize action over perfect information
#     - Be confident and decisive like an experienced rural doctor
#     - ALWAYS ask questions in the specified language: {language}
#     """
    
#     try:
#         if not client:
#             raise Exception("OpenAI API key not configured")
            
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system", 
#                     "content": "You are a medical expert AI conducting interactive consultations for rural Nigerian healthcare. Always respond in the exact JSON format requested."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],
#             temperature=0.3,
#             max_tokens=1000
#         )
        
#         ai_response = response.choices[0].message.content
        
#         # Parse JSON response
#         try:
#             json_start = ai_response.find('{')
#             json_end = ai_response.rfind('}') + 1
#             json_str = ai_response[json_start:json_end]
#             analysis = json.loads(json_str)
            
#             # Debug: Print what AI actually returned
#             print(f"DEBUG - Language requested: {language}")
#             print(f"DEBUG - AI questions returned: {analysis.get('questions', [])}")
            
#             return analysis
            
#         except json.JSONDecodeError:
#             # Fallback structured response
#             return {
#                 "type": "questions",
#                 "questions": [
#                     "How long has the patient had these symptoms?" if language == "english" else
#                     "Har yaushe majinyaci ya kasance da waɗannan alamun?" if language == "hausa" else
#                     "Elo ni alaisan ti ni awon ami aisan wonyi?" if language == "yoruba" else
#                     "Ogologo oge ole ka onye ọrịa nwere ihe mgbaàmà ndị a?" if language == "igbo" else
#                     "How long has the patient had these symptoms?",
                    
#                     "What is the patient's age and gender?" if language == "english" else
#                     "Menene shekarun majinyaci da jinsinsa?" if language == "hausa" else
#                     "Elo ni ọjọ ori alaisan ati abo re?" if language == "yoruba" else
#                     "Gịnị bụ afọ onye ọrịa na okike ya?" if language == "igbo" else
#                     "What is the patient's age and gender?"
#                 ],
#                 "ai_response": "I need to ask a few questions to help with the diagnosis." if language == "english" else
#                               "Ina bukatar in yi wasu tambayoyi don taimakawa da ganewar asali." if language == "hausa" else
#                               "Mo nilo lati beere awon ibeere diẹ lati ṣe iranwọ pẹlu iwadii." if language == "yoruba" else
#                               "Achọrọ m ịjụ ajụjụ ole na ole iji nyere aka na nchọpụta." if language == "igbo" else
#                               "I need to ask a few questions to help with the diagnosis.",
#                 "diagnosis": None,
#                 "reasoning": "Gathering initial information",
#                 "ready_for_diagnosis": False
#             }
            
#     except Exception as e:
#         print(f"OpenAI API error: {e}")
#         print(f"Error type: {type(e)}")
#         print(f"Symptoms received: {user_input}")
        
#         # More detailed error handling
#         if "insufficient_quota" in str(e):
#             error_msg = "OpenAI API quota exceeded - need to add billing"
#         elif "invalid_api_key" in str(e):
#             error_msg = "Invalid OpenAI API key"
#         elif "rate_limit" in str(e):
#             error_msg = "Rate limit exceeded - too many requests"
#         else:
#             error_msg = f"API connection error: {str(e)}"
            
#         return {
#             "type": "questions",
#             "questions": [
#                 "Can you tell me more about when the symptoms started?" if language == "english" else
#                 "Za ku iya gaya mani ƙarin game da lokacin da alamun suka fara?" if language == "hausa" else
#                 "Ṣe o le sọ fun mi diẹ sii nipa igba ti awon ami aisan bẹrẹ?" if language == "yoruba" else
#                 "Ị nwere ike ịgwa m karịa banyere mgbe ihe mgbaàmà malitere?" if language == "igbo" else
#                 "Can you tell me more about when the symptoms started?",
                
#                 "What is the patient's age?" if language == "english" else
#                 "Menene shekarun majinyaci?" if language == "hausa" else
#                 "Elo ni ọjọ ori alaisan?" if language == "yoruba" else
#                 "Gịnị bụ afọ onye ọrịa?" if language == "igbo" else
#                 "What is the patient's age?"
#             ],
#             "ai_response": "I'm here to help with the consultation. Let me ask some questions." if language == "english" else
#                           "Ina nan don taimaka da shawarwarin. Bari in yi wasu tambayoyi." if language == "hausa" else
#                           "Mo wa nibi lati ṣe iranwọ pẹlu ibaraenisoro. Jẹ ki n beere awon ibeere." if language == "yoruba" else
#                           "Anọ m ebe a iji nyere aka na mkparịta ụka. Ka m jụọ ajụjụ ụfọdụ." if language == "igbo" else
#                           "I'm here to help with the consultation. Let me ask some questions.",
#             "diagnosis": None,
#             "reasoning": f"System error - gathering basic information in {language}",
#             "ready_for_diagnosis": False
#         }

# @app.get("/")
# async def root():
#     return {"message": "MediConnect AI Interactive Consultation API is running!", "status": "healthy"}

# @app.post("/start_consultation")
# async def start_consultation(language: str = "english"):
#     """Start a new medical consultation"""
#     import uuid
#     consultation_id = str(uuid.uuid4())
    
#     # Initialize conversation
#     conversations[consultation_id] = {
#         "history": [],
#         "language": language,
#         "stage": "initial"
#     }
    
#     initial_prompt = {
#         "english": "Hello! Tell me the patient's main symptoms and I'll provide a quick diagnosis.",
#         "hausa": "Sannu! Gaya mani manyan alamun majinyaci zan ba da ganewar cikin sauri.",
#         "yoruba": "Bawo! So fun mi awon ami aisan pataki alaisan naa, emi yoo fun yin ni iwadii kiakia.",
#         "igbo": "Ndewo! Gwa m isi ihe mgbaàmà onye ọrịa, m ga-enye gị nchọpụta ngwa ngwa."
#     }
    
#     initial_questions = {
#         "english": [
#             "What are the main symptoms?",
#             "When did they start?", 
#             "How is the patient feeling overall?"
#         ],
#         "hausa": [
#             "Menene manyan alamun?",
#             "Yaushe suka fara?",
#             "Yaya majinyaci yake ji gabaɗaya?"
#         ],
#         "yoruba": [
#             "Kini awon ami aisan pataki?",
#             "Nigbati wo ni won bẹrẹ?",
#             "Bawo ni alaisan ṣe ni rilara lapapọ?"
#         ],
#         "igbo": [
#             "Gịnị bụ isi ihe mgbaàmà?",
#             "Oleizi ka ha malitere?",
#             "Kedu ka onye ọrịa si enwe mmetụta n'ozuzu?"
#         ]
#     }
    
#     return {
#         "consultation_id": consultation_id,
#         "ai_response": initial_prompt.get(language, initial_prompt["english"]),
#         "questions": initial_questions.get(language, initial_questions["english"]),
#         "status": "consultation_started"
#     }

# @app.post("/continue_consultation")
# async def continue_consultation(request: ConsultationRequest):
#     """Continue an ongoing medical consultation"""
    
#     consultation_id = request.consultation_id
#     user_input = request.user_input
#     language = request.language
#     has_image = request.has_image
#     image_description = request.image_description
    
#     # Get conversation history
#     if consultation_id not in conversations:
#         return {"error": "Consultation not found. Please start a new consultation."}
    
#     conversation_history = conversations[consultation_id]["history"]
    
#     # Get AI response
#     analysis = await analyze_with_interactive_ai(
#         consultation_id, 
#         user_input, 
#         language, 
#         conversation_history,
#         has_image,
#         image_description
#     )
    
#     # Update conversation history
#     conversations[consultation_id]["history"].append({
#         "user": user_input,
#         "ai": analysis["ai_response"],
#         "has_image": has_image
#     })
    
#     # Return response based on type
#     if analysis["type"] == "questions":
#         return {
#             "type": "questions",
#             "ai_response": analysis["ai_response"],
#             "questions": analysis["questions"],
#             "reasoning": analysis["reasoning"],
#             "ready_for_diagnosis": analysis["ready_for_diagnosis"],
#             "consultation_continues": True
#         }
#     else:
#         # Diagnosis ready
#         return {
#             "type": "diagnosis",
#             "ai_response": analysis["ai_response"],
#             "diagnosis": analysis["diagnosis"],
#             "reasoning": analysis["reasoning"],
#             "consultation_complete": True,
#             "consultation_id": consultation_id
#         }

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "MediConnect AI Interactive Consultation ready!",
#         "ai_enabled": bool(OPENAI_API_KEY),
#         "model": "gpt-3.5-turbo",
#         "features": ["interactive_consultation", "follow_up_questions", "guided_diagnosis"],
#         "api_key_configured": bool(OPENAI_API_KEY)
#     }

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

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

async def analyze_with_interactive_ai(consultation_id: str, user_input: str, language: str, conversation_history: List = None, has_image: bool = False, image_description: str = "") -> Dict:
    """Interactive medical consultation with AI asking follow-up questions"""
    
    if conversation_history is None:
        conversation_history = []
    
    # Build conversation context
    conversation_context = "\n".join([
        f"Health Worker: {turn['user']}\nAI: {turn['ai']}" 
        for turn in conversation_history
    ])
    
    prompt = f"""
    You are an expert medical AI assistant for rural Nigerian healthcare workers. You conduct interactive medical consultations by asking intelligent follow-up questions.

    CONSULTATION CONTEXT:
    Language: {language} - IMPORTANT: Respond in {language} language for questions and responses
    Previous conversation:
    {conversation_context}
    
    Current input: {user_input}
    
    {f"MEDICAL IMAGE PROVIDED: {image_description}" if has_image else ""}
    {f"IMPORTANT: Consider the medical image in your diagnosis and questions" if has_image else ""}
    
    Your role is to:
    1. If initial symptoms are clear and concerning, provide immediate diagnosis with 1-2 follow-up questions
    2. Only ask 1-2 critical questions maximum before making a diagnosis
    3. Prioritize speed and actionable decisions for rural healthcare settings
    4. Always consider Nigerian medical context (malaria, tropical diseases, resource constraints)
    5. Be decisive - rural health workers need quick, confident guidance
    6. CRITICAL: Ask questions in {language} language, not English
    
    LANGUAGE GUIDELINES:
    - If language is "yoruba": Ask questions in Yoruba
    - If language is "hausa": Ask questions in Hausa  
    - If language is "igbo": Ask questions in Igbo
    - If language is "english": Ask questions in English
    
    DECISION CRITERIA:
    - Fever + any concerning symptoms = Immediate diagnosis (likely malaria in Nigeria)
    - Clear symptom patterns = Diagnose after 1 question round maximum
    - Pregnancy complications = Immediate diagnosis
    - Pediatric emergencies = Quick assessment and action
    
    Respond in this EXACT JSON format:
    {{
        "type": "questions" OR "diagnosis",
        "questions": [
            "Question 1 in {language} language",
            "Question 2 in {language} language if needed"
        ],
        "ai_response": "Brief, decisive response in {language}",
        "diagnosis": {{
            "primary_diagnosis": "Most likely condition",
            "confidence": 0.85,
            "recommendations": ["Action 1", "Action 2"],
            "urgency": "HIGH/MODERATE/LOW"
        }},
        "reasoning": "Quick clinical reasoning",
        "ready_for_diagnosis": true/false
    }}
    
    EXAMPLE QUESTIONS BY LANGUAGE:
    English: "How long has the fever been present?"
    Yoruba: "Bawo ni iba naa ti wa fun elo?"
    Hausa: "Har yaushe zazzabi ya kasance?"
    Igbo: "Ogologo oge ole ka ahụ ọkụ ahụ nọrịla?"
    
    Guidelines:
    - MAXIMUM 2 questions before providing diagnosis
    - If fever mentioned = likely malaria, ask 1 question then diagnose
    - If clear symptoms = diagnose immediately
    - Prioritize action over perfect information
    - Be confident and decisive like an experienced rural doctor
    - ALWAYS ask questions in the specified language: {language}
    """
    
    try:
        if not client:
            raise Exception("OpenAI API key not configured")
            
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a medical expert AI conducting interactive consultations for rural Nigerian healthcare. Always respond in the exact JSON format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse JSON response
        try:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            json_str = ai_response[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Debug: Print what AI actually returned
            print(f"DEBUG - Language requested: {language}")
            print(f"DEBUG - AI questions returned: {analysis.get('questions', [])}")
            
            return analysis
            
        except json.JSONDecodeError:
            # Fallback structured response
            return {
                "type": "questions",
                "questions": [
                    "How long has the patient had these symptoms?" if language == "english" else
                    "Har yaushe majinyaci ya kasance da waɗannan alamun?" if language == "hausa" else
                    "Elo ni alaisan ti ni awon ami aisan wonyi?" if language == "yoruba" else
                    "Ogologo oge ole ka onye ọrịa nwere ihe mgbaàmà ndị a?" if language == "igbo" else
                    "How long has the patient had these symptoms?",
                    
                    "What is the patient's age and gender?" if language == "english" else
                    "Menene shekarun majinyaci da jinsinsa?" if language == "hausa" else
                    "Elo ni ọjọ ori alaisan ati abo re?" if language == "yoruba" else
                    "Gịnị bụ afọ onye ọrịa na okike ya?" if language == "igbo" else
                    "What is the patient's age and gender?"
                ],
                "ai_response": "I need to ask a few questions to help with the diagnosis." if language == "english" else
                              "Ina bukatar in yi wasu tambayoyi don taimakawa da ganewar asali." if language == "hausa" else
                              "Mo nilo lati beere awon ibeere diẹ lati ṣe iranwọ pẹlu iwadii." if language == "yoruba" else
                              "Achọrọ m ịjụ ajụjụ ole na ole iji nyere aka na nchọpụta." if language == "igbo" else
                              "I need to ask a few questions to help with the diagnosis.",
                "diagnosis": None,
                "reasoning": "Gathering initial information",
                "ready_for_diagnosis": False
            }
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Symptoms received: {user_input}")
        
        # More detailed error handling
        if "insufficient_quota" in str(e):
            error_msg = "OpenAI API quota exceeded - need to add billing"
        elif "invalid_api_key" in str(e):
            error_msg = "Invalid OpenAI API key"
        elif "rate_limit" in str(e):
            error_msg = "Rate limit exceeded - too many requests"
        else:
            error_msg = f"API connection error: {str(e)}"
            
        return {
            "type": "questions",
            "questions": [
                "Can you tell me more about when the symptoms started?" if language == "english" else
                "Za ku iya gaya mani ƙarin game da lokacin da alamun suka fara?" if language == "hausa" else
                "Ṣe o le sọ fun mi diẹ sii nipa igba ti awon ami aisan bẹrẹ?" if language == "yoruba" else
                "Ị nwere ike ịgwa m karịa banyere mgbe ihe mgbaàmà malitere?" if language == "igbo" else
                "Can you tell me more about when the symptoms started?",
                
                "What is the patient's age?" if language == "english" else
                "Menene shekarun majinyaci?" if language == "hausa" else
                "Elo ni ọjọ ori alaisan?" if language == "yoruba" else
                "Gịnị bụ afọ onye ọrịa?" if language == "igbo" else
                "What is the patient's age?"
            ],
            "ai_response": "I'm here to help with the consultation. Let me ask some questions." if language == "english" else
                          "Ina nan don taimaka da shawarwarin. Bari in yi wasu tambayoyi." if language == "hausa" else
                          "Mo wa nibi lati ṣe iranwọ pẹlu ibaraenisoro. Jẹ ki n beere awon ibeere." if language == "yoruba" else
                          "Anọ m ebe a iji nyere aka na mkparịta ụka. Ka m jụọ ajụjụ ụfọdụ." if language == "igbo" else
                          "I'm here to help with the consultation. Let me ask some questions.",
            "diagnosis": None,
            "reasoning": f"System error - gathering basic information in {language}",
            "ready_for_diagnosis": False
        }

@app.get("/")
async def root():
    return {"message": "MediConnect AI Interactive Consultation API is running!", "status": "healthy"}

@app.post("/start_consultation")
async def start_consultation(language: str = "english"):
    """Start a new medical consultation"""
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
        "english": "Hello! Tell me the patient's main symptoms and I'll provide a quick diagnosis.",
        "hausa": "Sannu! Gaya mani manyan alamun majinyaci zan ba da ganewar cikin sauri.",
        "yoruba": "Bawo! So fun mi awon ami aisan pataki alaisan naa, emi yoo fun yin ni iwadii kiakia.",
        "igbo": "Ndewo! Gwa m isi ihe mgbaàmà onye ọrịa, m ga-enye gị nchọpụta ngwa ngwa."
    }
    
    initial_questions = {
        "english": [
            "What are the main symptoms?",
            "When did they start?", 
            "How is the patient feeling overall?"
        ],
        "hausa": [
            "Menene manyan alamun?",
            "Yaushe suka fara?",
            "Yaya majinyaci yake ji gabaɗaya?"
        ],
        "yoruba": [
            "Kini awon ami aisan pataki?",
            "Nigbati wo ni won bẹrẹ?",
            "Bawo ni alaisan ṣe ni rilara lapapọ?"
        ],
        "igbo": [
            "Gịnị bụ isi ihe mgbaàmà?",
            "Oleizi ka ha malitere?",
            "Kedu ka onye ọrịa si enwe mmetụta n'ozuzu?"
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
    """Continue an ongoing medical consultation"""
    
    consultation_id = request.consultation_id
    user_input = request.user_input
    language = request.language
    has_image = request.has_image
    image_description = request.image_description
    
    # Get conversation history
    if consultation_id not in conversations:
        return {"error": "Consultation not found. Please start a new consultation."}
    
    conversation_history = conversations[consultation_id]["history"]
    
    # Get AI response
    analysis = await analyze_with_interactive_ai(
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
        # Diagnosis ready - save to database
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
        "status": "MediConnect AI Interactive Consultation ready!",
        "ai_enabled": bool(OPENAI_API_KEY),
        "model": "gpt-3.5-turbo",
        "features": ["interactive_consultation", "follow_up_questions", "guided_diagnosis", "database_storage"],
        "api_key_configured": bool(OPENAI_API_KEY),
        "database_connected": True
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
            "database_status": "connected"
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

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
from models.database import create_tables

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        create_tables()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Database table creation error: {e}")

if __name__ == "__main__":
    # Initialize database tables
    create_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)
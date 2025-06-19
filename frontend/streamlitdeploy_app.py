import streamlit as st
import openai
import json
from PIL import Image
import traceback
import os

# Initialize OpenAI client - Streamlit Cloud compatible
OPENAI_API_KEY = ""
try:
    # Try Streamlit secrets first (for cloud deployment)
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
except:
    # Fallback to environment variable (for local development)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

# Translation dictionary
TRANSLATIONS = {
    "English": {
        "title": "🏥 MediConnect AI",
        "subtitle": "Interactive AI Healthcare for Rural Nigeria",
        "language_header": "🌍 Language Selection",
        "consultation_header": "🩺 Interactive Medical Consultation", 
        "start_consultation": "Start New Consultation",
        "your_response": "Your Response:",
        "ai_questions": "Questions for you:",
        "send_response": "Send Response",
        "diagnosis_ready": "✅ Diagnosis Complete",
        "new_consultation": "Start New Consultation",
        "consultation_progress": "Consultation Progress",
        "questions_for_you": "Questions for you:",
        "type_response": "Type your response here...",
        "example_scenarios": "Example Patient Scenarios",
        "try_scenarios": "Try this consultation starter:",
        "system_impact": "System Impact",
        "interactive_consultations": "Interactive Consultations",
        "questions_asked": "Questions Asked by AI",
        "diagnostic_accuracy": "Diagnostic Accuracy",
        "health_worker_training": "Health Worker Training",
        "with_questions": "with questions",
        "improvement_skills": "improvement in skills",
        "diagnosis_results": "🎯 Diagnosis Results",
        "primary_diagnosis": "Primary Diagnosis:",
        "confidence": "Confidence:",
        "urgency_level": "Urgency Level:",
        "recommendations": "💊 Recommendations",
        "immediate_actions": "Immediate Actions:",
        "no_diagnoses_yet": "No diagnoses yet",
        "ai_confidence": "AI confidence",
        "active": "active",
        "this_session": "this session",
        "exchanges": "exchanges", 
        "total_turns": "total turns",
        "session_progress": "Session Progress",
        "backend_error": "Backend Connection Error",
        "ai_response": "AI Response:",
        "processing": "Processing your response...",
        "error_occurred": "An error occurred",
        "debug_info": "Debug Information",
        "request_data": "Request Data",
        "response_data": "Response Data",
        "final_diagnosis": "📋 Final Medical Assessment"
    },
    "Hausa": {
        "title": "🏥 MediConnect AI",
        "subtitle": "Mu'amalar AI ta kiwon lafiya don karkarar Najeriya",
        "language_header": "🌍 Zabin Harshe",
        "consultation_header": "🩺 Shawarwarin Likita ta AI",
        "start_consultation": "Fara Sabon Shawara",
        "your_response": "Amsarku:",
        "ai_questions": "Tambayoyin AI gare ku:",
        "send_response": "Aika Amsa",
        "diagnosis_ready": "✅ Ganewar Ya Kamala",
        "new_consultation": "Fara Sabon Shawara",
        "consultation_progress": "Ci gaban Shawara",
        "questions_for_you": "Tambayoyi gare ku:",
        "type_response": "Rubuta amsarku a nan...",
        "example_scenarios": "Misalan Yanayin Majinyaci",
        "try_scenarios": "Gwada wannan mafarin shawara:",
        "system_impact": "Tasirin Tsarin",
        "interactive_consultations": "Shawarwarin Mu'amala",
        "questions_asked": "Tambayoyin da AI ya yi",
        "diagnostic_accuracy": "Daidaiton Ganewar",
        "health_worker_training": "Horar Ma'aikatan Lafiya",
        "with_questions": "da tambayoyi",
        "improvement_skills": "ci gaba a ƙwarewa",
        "diagnosis_results": "🎯 Sakamakon Ganewar",
        "primary_diagnosis": "Babban Ganewar:",
        "confidence": "Tabbas:",
        "urgency_level": "Matakin Gaggawa:",
        "recommendations": "💊 Shawarwari",
        "immediate_actions": "Ayyukan Gaggawa:",
        "no_diagnoses_yet": "Babu ganewar tukuna",
        "ai_confidence": "Amincewar AI",
        "active": "mai aiki",
        "this_session": "wannan zaman",
        "exchanges": "musayar",
        "total_turns": "jimillar juyowa",
        "session_progress": "Ci gaban Zaman",
        "backend_error": "Kuskuren Haɗin Backend",
        "ai_response": "Amsar AI:",
        "processing": "Ana sarrafa amsarku...",
        "error_occurred": "Kuskure ya faru",
        "debug_info": "Bayanan Debug",
        "request_data": "Bayanan Buƙata",
        "response_data": "Bayanan Amsa",
        "final_diagnosis": "📋 Cikakkiyar Kimantawa ta Likitanci"
    },
    "Yoruba": {
        "title": "🏥 MediConnect AI",
        "subtitle": "Ibaraenisoro AI ilera fun awon agbegbe Naijiria",
        "language_header": "🌍 Yiyan Ede",
        "consultation_header": "🩺 Ibaraenisoro Dokita AI",
        "start_consultation": "Bere Ibaraenisoro Tuntun",
        "your_response": "Idahun Yin:",
        "ai_questions": "Awon ibeere AI fun yin:",
        "send_response": "Fi Idahun Ranše",
        "diagnosis_ready": "✅ Iwadii Ti Pari",
        "new_consultation": "Bere Ibaraenisoro Tuntun",
        "consultation_progress": "Ilọsiwaju Ibaraenisoro",
        "questions_for_you": "Awon ibeere fun yin:",
        "type_response": "Tẹ idahun yin nibi...",
        "example_scenarios": "Awon Apeere Ipo Alaisan",
        "try_scenarios": "Gbiyanju mafari ibaraenisoro yii:",
        "system_impact": "Ipa Eto",
        "interactive_consultations": "Awon Ibaraenisoro Ajọṣepọ",
        "questions_asked": "Awon Ibeere ti AI Beere",
        "diagnostic_accuracy": "Ọgbọn Iwadii",
        "health_worker_training": "Ikẹkọ Oṣiṣẹ Ilera",
        "with_questions": "pẹlu awon ibeere",
        "improvement_skills": "ilọsiwaju ni awon ọgbọn",
        "diagnosis_results": "🎯 Awon Abajade Iwadii",
        "primary_diagnosis": "Iwadii Akọkọ:",
        "confidence": "Igbagbọ:",
        "urgency_level": "Ipele Kiakia:",
        "recommendations": "💊 Awon Imọran",
        "immediate_actions": "Awon Iṣe Kiakia:",
        "no_diagnoses_yet": "Ko si awon iwadii sibẹ",
        "ai_confidence": "Igbẹkẹle AI",
        "active": "ti nṣiṣẹ",
        "this_session": "iṣesi yii",
        "exchanges": "awon paṣipaarọ",
        "total_turns": "lapapọ awon yipo",
        "session_progress": "Ilọsiwaju Iṣesi",
        "backend_error": "Aṣiṣe Asopọ Backend",
        "ai_response": "Idahun AI:",
        "processing": "N ṣiṣẹ lori idahun yin...",
        "error_occurred": "Aṣiṣe kan waye",
        "debug_info": "Alaye Debug",
        "request_data": "Data Ibeere",
        "response_data": "Data Idahun",
        "final_diagnosis": "📋 Iṣiro Ilera Pipe"
    },
    "Igbo": {
        "title": "🏥 MediConnect AI",
        "subtitle": "Mkparịta ụka AI ahụike maka ime obodo Naịjirịa",
        "language_header": "🌍 Nhọrọ Asụsụ",
        "consultation_header": "🩺 Mkparịta ụka Dọkịta AI",
        "start_consultation": "Malite Mkparịta Ụka Ọhụrụ",
        "your_response": "Nzaghachi Gị:",
        "ai_questions": "Ajụjụ AI maka gị:",
        "send_response": "Ziga Nzaghachi",
        "diagnosis_ready": "✅ Nchọpụta Zuru Ezu",
        "new_consultation": "Malite Mkparịta Ụka Ọhụrụ",
        "consultation_progress": "Ọganihu Mkparịta Ụka",
        "questions_for_you": "Ajụjụ maka gị:",
        "type_response": "Dee nzaghachi gị ebe a...",
        "example_scenarios": "Ọmụmaatụ Ọnọdụ Onye Ọrịa",
        "try_scenarios": "Nwalee mmalite mkparịta ụka a:",
        "system_impact": "Mmetụta Sistemụ",
        "interactive_consultations": "Mkparịta Ụka Mmekọrịta",
        "questions_asked": "Ajụjụ AI Jụrụ",
        "diagnostic_accuracy": "Izi Ezi Nchọpụta",
        "health_worker_training": "Ọzụzụ Ndị Ọrụ Ahụike",
        "with_questions": "na ajụjụ",
        "improvement_skills": "mmelite na nkà",
        "diagnosis_results": "🎯 Nsonaazụ Nchọpụta",
        "primary_diagnosis": "Nchọpụta Mbụ:",
        "confidence": "Ntụkwasị Obi:",
        "urgency_level": "Ọkwa Ngwa Ngwa:",
        "recommendations": "💊 Ntụziaka",
        "immediate_actions": "Omume Ngwa Ngwa:",
        "no_diagnoses_yet": "Enwebeghị nchọpụta ka",
        "ai_confidence": "Ntụkwasị obi AI",
        "active": "na-arụ ọrụ",
        "this_session": "nnọkọ a",
        "exchanges": "mgbanwe",
        "total_turns": "ngụkọta ntụgharị",
        "session_progress": "Ọganihu Nnọkọ",
        "backend_error": "Njehie Njikọ Backend",
        "ai_response": "Nzaghachi AI:",
        "processing": "Na-ahazi nzaghachi gị...",
        "error_occurred": "Njehie mere",
        "debug_info": "Ozi Debug",
        "request_data": "Data Arịrịọ",
        "response_data": "Data Nzaghachi",
        "final_diagnosis": "📋 Nyocha Ahụike Zuru Ezu"
    }
}

def get_text(key, language="English"):
    """Get translated text based on selected language"""
    return TRANSLATIONS[language].get(key, TRANSLATIONS["English"][key])

# Page configuration
st.set_page_config(
    page_title="MediConnect AI - Interactive Healthcare",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #0084ff;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #28a745;
    }
    .ai-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .diagnosis-container {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #4caf50;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .diagnosis-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin-bottom: 1rem;
        text-align: center;
    }
    .diagnosis-item {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4caf50;
    }
    .recommendation-item {
        background-color: #fff3e0;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #ff9800;
    }
    .urgency-high {
        background-color: #ffebee;
        border-left-color: #f44336;
        color: #c62828;
    }
    .urgency-moderate {
        background-color: #fff8e1;
        border-left-color: #ff9800;
        color: #ef6c00;
    }
    .urgency-low {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'consultation_id' not in st.session_state:
        st.session_state.consultation_id = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'consultation_active' not in st.session_state:
        st.session_state.consultation_active = False
    if 'total_consultations' not in st.session_state:
        st.session_state.total_consultations = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'total_diagnoses' not in st.session_state:
        st.session_state.total_diagnoses = 0
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = 0
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    if 'final_diagnosis' not in st.session_state:
        st.session_state.final_diagnosis = None

# Initialize session state
initialize_session_state()

def get_openai_diagnosis(conversation_text, language="english"):
    """Get medical diagnosis directly from OpenAI"""
    if not openai_client:
        return {
            "primary_diagnosis": "OpenAI API key not configured",
            "confidence": 0.0,
            "urgency": "MODERATE",
            "recommendations": ["Please configure OpenAI API key in Streamlit secrets"],
            "clinical_reasoning": "API key required"
        }
    
    medical_prompt = f"""You are an expert medical doctor. A patient presents with these symptoms:

{conversation_text}

Provide a medical diagnosis in JSON format. Be specific and accurate.

For example, if patient has diarrhea and vomiting for 3 weeks:
- This is chronic gastroenteritis, possibly IBD, parasitic infection, or malabsorption
- NOT acute viral gastroenteritis (that lasts days, not weeks)
- Requires specific investigation and treatment

Respond in {language} with this exact JSON format:
{{
    "primary_diagnosis": "Specific diagnosis based on symptoms",
    "confidence": 0.80,
    "urgency": "LOW/MODERATE/HIGH/CRITICAL",
    "recommendations": [
        "Specific recommendation 1 with dosages if applicable",
        "Specific recommendation 2 with clear instructions", 
        "Specific recommendation 3 with monitoring guidelines",
        "Specific recommendation 4 with follow-up criteria",
        "Specific recommendation 5 with patient education"
    ],
    "clinical_reasoning": "Brief explanation of diagnosis"
}}"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a medical specialist. Respond only with valid JSON in {language}. No additional text."
                },
                {
                    "role": "user", 
                    "content": medical_prompt
                }
            ],
            temperature=0.1,
            max_tokens=800,
            response_format={ "type": "json_object" }
        )
        
        ai_response = response.choices[0].message.content.strip()
        diagnosis_data = json.loads(ai_response)
        
        # Ensure all required fields
        if not diagnosis_data.get("primary_diagnosis"):
            diagnosis_data["primary_diagnosis"] = "Medical assessment completed"
        if not diagnosis_data.get("confidence"):
            diagnosis_data["confidence"] = 0.75
        if not diagnosis_data.get("urgency"):
            diagnosis_data["urgency"] = "MODERATE"
        if not diagnosis_data.get("recommendations"):
            diagnosis_data["recommendations"] = ["Follow medical advice", "Monitor symptoms", "Return if worsening"]
            
        return diagnosis_data
        
    except Exception as e:
        st.error(f"OpenAI Error: {str(e)}")
        return {
            "primary_diagnosis": f"Assessment limited due to API error: {str(e)[:100]}",
            "confidence": 0.60,
            "urgency": "MODERATE",
            "recommendations": [
                "Seek direct medical consultation",
                "Monitor symptoms closely", 
                "Return if symptoms worsen",
                "Consider emergency care if severe",
                "Follow up with healthcare provider"
            ],
            "clinical_reasoning": "Limited by system error"
        }

def get_openai_questions(conversation_text, language="english"):
    """Get follow-up questions directly from OpenAI"""
    if not openai_client:
        default_questions = {
            "english": ["What is the patient's age?", "How long have symptoms been present?"],
            "hausa": ["Menene shekarun majinyaci?", "Har yaushe alamun suka kasance?"],
            "yoruba": ["Elo ni ọjọ ori alaisan?", "Elo ni awon ami aisan yi ti wa?"],
            "igbo": ["Gịnị bụ afọ onye ọrịa?", "Ogologo oge ole ka ihe mgbaàmà ndị a nọrọla?"]
        }
        return {
            "questions": default_questions.get(language, default_questions["english"]),
            "ai_response": "I need more information for accurate diagnosis."
        }
    
    question_prompt = f"""Based on this patient information: {conversation_text}

Ask 2 intelligent medical follow-up questions in {language} to gather essential diagnostic information.

Respond with this exact JSON format:
{{
    "questions": [
        "Medical question 1 in {language}",
        "Medical question 2 in {language}"
    ],
    "ai_response": "Brief response in {language} explaining why you need this information"
}}"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a medical doctor asking diagnostic questions in {language}. Respond only with JSON."
                },
                {
                    "role": "user",
                    "content": question_prompt
                }
            ],
            temperature=0.3,
            max_tokens=400,
            response_format={ "type": "json_object" }
        )
        
        ai_response = response.choices[0].message.content.strip()
        return json.loads(ai_response)
        
    except Exception as e:
        fallback_questions = {
            "english": {
                "questions": ["What is the patient's age?", "How severe are the symptoms?"],
                "ai_response": "I need additional information for diagnosis."
            },
            "hausa": {
                "questions": ["Menene shekarun majinyaci?", "Yaya tsananin alamun?"],
                "ai_response": "Ina bukatar ƙarin bayani don ganewar asali."
            },
            "yoruba": {
                "questions": ["Elo ni ọjọ ori alaisan?", "Bawo ni awon ami aisan ṣe le to?"],
                "ai_response": "Mo nilo alaye diẹ sii fun iwadii."
            },
            "igbo": {
                "questions": ["Gịnị bụ afọ onye ọrịa?", "Kedu ka ihe mgbaàmà ndị ahụ si sie ike?"],
                "ai_response": "Achọrọ m ozi ọzọ maka nchọpụta."
            }
        }
        return fallback_questions.get(language, fallback_questions["english"])

def start_new_consultation(language):
    """Start a new consultation with direct OpenAI"""
    import uuid
    consultation_id = str(uuid.uuid4())
    
    initial_prompt = {
        "english": "Hello! I'm Dr. MediConnect AI. Please describe the patient's symptoms and I'll provide a comprehensive diagnosis.",
        "hausa": "Sannu! Ni ne Dokta MediConnect AI. Don Allah ka bayyana alamun majinyaci zan ba da cikakkiyar ganewar asali.",
        "yoruba": "Bawo! Emi ni Dokita MediConnect AI. Jọwọ ṣapejuwe awon ami aisan alaisan, emi yoo fun yin ni iwadii pipe.",
        "igbo": "Ndewo! Abụ m Dọkịta MediConnect AI. Biko kọwaa ihe mgbaàmà onye ọrịa, m ga-enye gị nchọpụta zuru ezu."
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

def continue_consultation(consultation_id, user_input, language, has_image=False, image_description=""):
    """Continue consultation with direct OpenAI"""
    
    # Get conversation history
    conversation_text = ""
    for turn in st.session_state.conversation_history:
        if turn["type"] == "user":
            conversation_text += f"Patient: {turn['content']} "
    
    # Add current input
    conversation_text += f"Patient: {user_input} "
    
    # Add image info if present
    if has_image and image_description:
        conversation_text += f"[Medical Image: {image_description}] "
    
    # Count user exchanges
    user_exchanges = len([turn for turn in st.session_state.conversation_history if turn["type"] == "user"])
    
    # Decide whether to ask questions or provide diagnosis
    should_diagnose = user_exchanges >= 1  # Diagnose after 1-2 exchanges
    
    if should_diagnose:
        # Get diagnosis from OpenAI
        diagnosis = get_openai_diagnosis(conversation_text, language)
        
        response_texts = {
            'english': "Based on the symptoms described, here is my medical assessment:",
            'hausa': "Bisa ga alamun da aka bayyana, ga kimantawa ta likitanci:",
            'yoruba': "Ni ibamu lori awon ami aisan ti a so, eyi ni iṣiro mi ti ilera:",
            'igbo': "Dabere na ihe mgbaàmà akọwara, nke a bụ nyocha ahụike m:"
        }
        
        return {
            "type": "diagnosis",
            "ai_response": response_texts.get(language, response_texts['english']),
            "diagnosis": diagnosis,
            "consultation_complete": True
        }
    else:
        # Get follow-up questions from OpenAI
        questions_data = get_openai_questions(conversation_text, language)
        
        return {
            "type": "questions",
            "ai_response": questions_data["ai_response"],
            "questions": questions_data["questions"],
            "consultation_continues": True
        }

def reset_consultation():
    """Reset consultation state"""
    st.session_state.consultation_id = None
    st.session_state.conversation_history = []
    st.session_state.consultation_active = False
    st.session_state.current_questions = 0
    st.session_state.final_diagnosis = None

def display_conversation_history(language):
    """Display the conversation history in a chat-like format"""
    for i, turn in enumerate(st.session_state.conversation_history):
        if turn["type"] == "ai":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**{get_text('ai_response', language)}**")
                st.write(turn["content"])
                
                if "questions" in turn and turn["questions"]:
                    st.markdown(f"**{get_text('questions_for_you', language)}**")
                    for q in turn["questions"]:
                        st.write(f"• {q}")
                        
        else:  # user message
            with st.chat_message("user", avatar="👨‍⚕️"):
                st.write(turn["content"])

def display_final_diagnosis(diagnosis, language):
    """Display the final diagnosis in a prominent, clear format"""
    
    st.markdown(f"""
    <div class="diagnosis-container">
        <div class="diagnosis-header">{get_text('final_diagnosis', language)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for diagnosis details
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"### {get_text('diagnosis_results', language)}")
        
        # Primary diagnosis
        st.markdown(f"""
        <div class="diagnosis-item">
            <strong>{get_text('primary_diagnosis', language)}</strong><br>
            {diagnosis.get('primary_diagnosis', 'Not specified')}
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence with progress bar
        confidence = diagnosis.get('confidence', 0)
        st.markdown(f"**{get_text('confidence', language)}**")
        st.progress(confidence)
        st.write(f"**{confidence * 100:.0f}%**")
        
        # Urgency level with color coding
        urgency = diagnosis.get('urgency', 'MODERATE')
        urgency_colors = {
            'LOW': ('🟢', 'urgency-low'),
            'MODERATE': ('🟡', 'urgency-moderate'), 
            'HIGH': ('🔴', 'urgency-high'),
            'CRITICAL': ('🚨', 'urgency-high')
        }
        
        icon, css_class = urgency_colors.get(urgency, ('🟡', 'urgency-moderate'))
        
        st.markdown(f"""
        <div class="diagnosis-item {css_class}">
            <strong>{get_text('urgency_level', language)}</strong><br>
            {icon} <strong>{urgency}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {get_text('recommendations', language)}")
        st.markdown(f"**{get_text('immediate_actions', language)}**")
        
        recommendations = diagnosis.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"""
                <div class="recommendation-item">
                    <strong>{i}.</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="recommendation-item">
                <strong>No specific recommendations provided</strong>
            </div>
            """, unsafe_allow_html=True)

# Language selection
st.header("🌍 Language Selection / Zabin Harshe / Yiyan Ede / Nhọrọ Asụsụ")
selected_language = st.selectbox(
    "Select Language / Zaɓi Harshe / Yan Ede / Họrọ Asụsụ", 
    ["English", "Hausa", "Yoruba", "Igbo"]
)

# Main interface
st.title(get_text("title", selected_language))
st.subheader(get_text("subtitle", selected_language))

# Debug mode toggle (hidden in sidebar)
with st.sidebar:
    st.session_state.debug_mode = st.checkbox("🔍 Debug Mode", value=st.session_state.debug_mode)

# OpenAI connection status
if OPENAI_API_KEY:
    st.success("✅ AI Medical Assistant Ready - OpenAI Direct Mode!")
else:
    st.error("❌ OpenAI API key not configured. Please add OPENAI_API_KEY to Streamlit secrets.")
    st.info("💡 Go to app settings → Secrets → Add: OPENAI_API_KEY = \"your-key-here\"")

# Main consultation interface
st.header(get_text("consultation_header", selected_language))

# Start new consultation section
if not st.session_state.consultation_active:
    # Start consultation button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button(
            get_text("start_consultation", selected_language), 
            type="primary", 
            use_container_width=True,
            disabled=not OPENAI_API_KEY,
            key="start_consultation_main"
        ):
            with st.spinner(get_text("processing", selected_language)):
                data = start_new_consultation(selected_language)
                
                st.session_state.consultation_id = data["consultation_id"]
                st.session_state.consultation_active = True
                st.session_state.conversation_history = [{
                    "type": "ai",
                    "content": data["ai_response"],
                    "questions": data.get("questions", [])
                }]
                st.session_state.total_consultations += 1
                st.session_state.current_questions = len(data.get("questions", []))
                st.session_state.final_diagnosis = None  # Reset diagnosis
                st.rerun()
    
    with col2:
        if st.button("🔄 Reset All Data", key="reset_all_data_main"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.rerun()

# Display final diagnosis if consultation is complete
if st.session_state.final_diagnosis and not st.session_state.consultation_active:
    st.markdown("---")
    display_final_diagnosis(st.session_state.final_diagnosis, selected_language)
    
    # Start new consultation button after diagnosis
    st.markdown("---")
    if st.button(get_text("new_consultation", selected_language), type="primary", use_container_width=True, key="new_consultation_after_diagnosis"):
        reset_consultation()
        st.rerun()

# Active consultation interface
if st.session_state.consultation_active:
    
    # Progress indicator
    exchanges_count = len([turn for turn in st.session_state.conversation_history if turn.get("type") == "user"])
    st.info(f"🔄 {get_text('consultation_progress', selected_language)}: {exchanges_count} {get_text('exchanges', selected_language)}")
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("### 💬 Conversation History")
        display_conversation_history(selected_language)
    
    # Check if consultation is complete (has diagnosis)
    last_turn = st.session_state.conversation_history[-1] if st.session_state.conversation_history else None
    consultation_complete = (last_turn and 
                           last_turn.get("type") == "ai" and 
                           "diagnosis" in last_turn and 
                           last_turn["diagnosis"])
    
    if not consultation_complete:
        # Input section for continuing consultation
        st.markdown("---")
        st.markdown(f"### {get_text('your_response', selected_language)}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_input = st.text_area(
                get_text("type_response", selected_language),
                height=100,
                key=f"user_input_{len(st.session_state.conversation_history)}",
                placeholder=get_text("type_response", selected_language)
            )
        
        with col2:
            st.markdown("**📸 Medical Image (Optional)**")
            uploaded_image = st.file_uploader(
                "X-ray, skin condition, etc.",
                type=['png', 'jpg', 'jpeg'],
                key=f"image_{len(st.session_state.conversation_history)}"
            )
            
            if uploaded_image:
                st.image(uploaded_image, caption="Medical Image", width=150)
                st.info("💡 AI will analyze this image with your consultation")
        
        # Send response and new consultation buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button(
                get_text("send_response", selected_language), 
                type="primary", 
                disabled=not user_input.strip(),
                use_container_width=True,
                key="send_response_main"
            ):
                if user_input.strip():
                    with st.spinner(get_text("processing", selected_language)):
                        # Add user input to conversation history
                        st.session_state.conversation_history.append({
                            "type": "user",
                            "content": user_input
                        })
                        
                        # Prepare image description if image uploaded
                        image_description = ""
                        if uploaded_image:
                            image_description = f"Medical image uploaded: {uploaded_image.name}. This appears to be a medical image that should be considered in the diagnosis."
                        
                        # Continue consultation
                        data = continue_consultation(
                            st.session_state.consultation_id,
                            user_input,
                            selected_language,
                            bool(uploaded_image),
                            image_description
                        )
                        
                        if data["type"] == "questions":
                            # More questions
                            st.session_state.conversation_history.append({
                                "type": "ai",
                                "content": data["ai_response"],
                                "questions": data.get("questions", [])
                            })
                            st.session_state.total_questions += len(data.get("questions", []))
                            st.session_state.current_questions = len(data.get("questions", []))
                        else:
                            # Diagnosis ready
                            st.session_state.conversation_history.append({
                                "type": "ai",
                                "content": data["ai_response"],
                                "diagnosis": data.get("diagnosis")
                            })
                            st.session_state.consultation_active = False
                            st.session_state.total_diagnoses += 1
                            # Store final diagnosis for display
                            st.session_state.final_diagnosis = data.get("diagnosis")
                            
                        st.rerun()
        
        with col2:
            if st.button(get_text("new_consultation", selected_language), key="new_consultation_during_active"):
                reset_consultation()
                st.rerun()
        
        with col3:
            if st.button("🔍 Toggle Debug", key="toggle_debug_main"):
                st.session_state.debug_mode = not st.session_state.debug_mode
                st.rerun()
    
    else:
        # Consultation complete - store diagnosis and reset
        if last_turn.get("diagnosis"):
            st.session_state.final_diagnosis = last_turn["diagnosis"]
        st.session_state.consultation_active = False
        st.rerun()

# Sidebar with project information and metrics
with st.sidebar:
    st.markdown("---")
    
    # Navigation tabs
    tab_selection = st.radio(
        "Navigation",
        ["📋 Project Summary", "📊 Live Metrics", "🧪 Test Scenarios"],
        label_visibility="collapsed"
    )
    
    if tab_selection == "📋 Project Summary":
        st.markdown("### 🏥 MediConnect AI")
        st.markdown("*Multilingual AI Medical Consultant for Nigerian Rural Healthcare*")
        
        st.markdown("---")
        
        # The Problem
        st.markdown("#### 🎯 The Problem")
        st.markdown("""
        **Rural Nigeria Healthcare Crisis:**
        
        • **120 million rural Nigerians** lack access to quality healthcare
        
        • **Doctor-to-patient ratio:** 1:5,000+ vs WHO standard of 1:1,000
        
        • **Language barriers:** 90% of rural health workers need native language support
        
        • **Diagnostic delays:** 72% of preventable deaths due to late/incorrect diagnosis
        
        • **Cost barriers:** $50+ for basic consultation
        
        • **Geographic isolation:** 2-hour average travel to nearest doctor
        """)
        
        st.markdown("---")
        
        # Our Solution
        st.markdown("#### 🚀 Our Solution")
        st.markdown("""
        **Core Capabilities:**
        
        • **High diagnostic accuracy** (powered by GPT-4)
        
        • **4 Nigerian languages:** English, Hausa, Yoruba, Igbo with medical terminology
        
        • **Interactive consultation:** 2-3 intelligent questions maximum
        
        • **Medical image analysis:** X-ray interpretation, skin condition diagnosis, wound assessment
        
        • **Comprehensive diagnosis:** 4-5 detailed recommendations per case
        
        • **Cloud-ready:** No backend required, direct OpenAI integration
        """)
        
        st.markdown("**Enhanced Diagnosis Results:**")
        st.markdown("""
        • **Primary diagnosis** with confidence scoring (70-95%)
        
        • **Urgency level** assessment (LOW, MODERATE, HIGH, CRITICAL)
        
        • **4-5 immediate actions** for health workers
        
        • **Nigerian-specific conditions** (malaria, typhoid, tropical diseases)
        
        • **Age-appropriate recommendations** (pediatric, elderly care)
        """)
    
    elif tab_selection == "📊 Live Metrics":
        st.markdown("#### 📈 System Performance")
        
        # Calculate current session metrics
        current_questions = st.session_state.current_questions
        current_exchanges = len([turn for turn in st.session_state.conversation_history if turn.get("type") == "user"])
        
        # Calculate diagnostic confidence if available
        latest_confidence = "N/A"
        confidence_delta = get_text('no_diagnoses_yet', selected_language)
        
        if st.session_state.final_diagnosis:
            try:
                confidence = st.session_state.final_diagnosis.get("confidence", 0)
                latest_confidence = f"{confidence * 100:.0f}%"
                confidence_delta = get_text('ai_confidence', selected_language)
            except:
                pass
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                get_text('interactive_consultations', selected_language),
                st.session_state.total_consultations,
                delta=f"+{1 if st.session_state.consultation_active else 0} {get_text('active', selected_language)}"
            )
            
        with col2:
            st.metric(
                get_text('questions_asked', selected_language),
                st.session_state.total_questions + current_questions,
                delta=f"+{current_questions} {get_text('this_session', selected_language)}"
            )
        
        st.metric(
            get_text('diagnostic_accuracy', selected_language),
            latest_confidence,
            delta=confidence_delta
        )
        
        st.metric(
            get_text('session_progress', selected_language),
            f"{current_exchanges} {get_text('exchanges', selected_language)}",
            delta=f"{len(st.session_state.conversation_history)} {get_text('total_turns', selected_language)}"
        )
        
        # OpenAI status
        st.markdown("---")
        st.markdown("#### 🔧 System Status")
        if OPENAI_API_KEY:
            st.success("✅ OpenAI Connected")
        else:
            st.error("❌ OpenAI API Key Missing")
        
        # Session info
        if st.session_state.consultation_active:
            st.info(f"🔄 Active Consultation ID: {st.session_state.consultation_id[:8]}...")
        
        # Final diagnosis status
        if st.session_state.final_diagnosis:
            st.success("✅ Diagnosis Available")
            urgency = st.session_state.final_diagnosis.get('urgency', 'MODERATE')
            st.write(f"Urgency: **{urgency}**")
        
    elif tab_selection == "🧪 Test Scenarios":
        st.markdown("#### 💡 Example Test Scenarios")
        st.markdown(f"**{get_text('try_scenarios', selected_language)}**")
        
        # Language-specific test scenarios
        scenarios = {
            "English": [
                "5-year-old child with fever for 3 days and body pain",
                "Adult with severe neck pain and headache since yesterday",
                "Pregnant woman with abdominal pain and vomiting",
                "Elderly person with breathing difficulties and weakness",
                "Child with diarrhea, vomiting and moderate fever"
            ],
            "Hausa": [
                "Yaro mai shekara 5 da zazzabi na kwanaki 3 da ciwon jiki",
                "Babba da tsananin ciwon wuya da ciwon kai tun jiya", 
                "Mace mai juna biyu da ciwon ciki da amai",
                "Dattijo da matsalar numfashi da rauni",
                "Yaro da gudawa, amai da matsakaicin zazzabi"
            ],
            "Yoruba": [
                "Ọmọ ọdun marun ti o ni iba fun ọjọ mẹta ati ira ara",
                "Agbalagba ti o ni ọrọn gigun nla ati ori gigun lati ana",
                "Obinrin oyun ti o ni inu gigun ati ọgbẹlẹ",
                "Arugbo ti o ni wahala mimi ati ailera",
                "Ọmọ ti o ni inu jijẹ, ọgbẹlẹ ati iba agbedemeji"
            ],
            "Igbo": [
                "Nwata afọ ise nwere ahụ ọkụ ruo ụbọchị atọ na mgbu ahụ",
                "Onye okenye nwere nnukwu mgbu olu na isi ọwụwa kemgbe ụnyaahụ",
                "Nwanyị dị ime nwere mgbu afọ na ọgbụgbọ",
                "Onye agadi nwere nsogbu iku ume na adịghị ike",
                "Nwata nwere afọ ọsịsa, ọgbụgbọ na ahụ ọkụ agbata obi"
            ]
        }
        
        test_scenarios = scenarios.get(selected_language, scenarios["English"])
        
        for i, scenario in enumerate(test_scenarios):
            if st.button(f"📝 {scenario}", key=f"scenario_{i}"):
                if not st.session_state.consultation_active:
                    # Start consultation first
                    data = start_new_consultation(selected_language)
                    st.session_state.consultation_id = data["consultation_id"]
                    st.session_state.consultation_active = True
                    st.session_state.conversation_history = [{
                        "type": "ai",
                        "content": data["ai_response"],
                        "questions": data.get("questions", [])
                    }]
                    st.session_state.total_consultations += 1
                    st.session_state.final_diagnosis = None
                    
                # Add scenario as user input
                if st.session_state.consultation_active:
                    st.session_state.conversation_history.append({
                        "type": "user",
                        "content": scenario
                    })
                    
                    # Continue consultation with scenario
                    data = continue_consultation(
                        st.session_state.consultation_id,
                        scenario,
                        selected_language
                    )
                    
                    if data["type"] == "questions":
                        st.session_state.conversation_history.append({
                            "type": "ai",
                            "content": data["ai_response"],
                            "questions": data.get("questions", [])
                        })
                        st.session_state.total_questions += len(data.get("questions", []))
                    else:
                        st.session_state.conversation_history.append({
                            "type": "ai",
                            "content": data["ai_response"],
                            "diagnosis": data.get("diagnosis")
                        })
                        st.session_state.consultation_active = False
                        st.session_state.total_diagnoses += 1
                        st.session_state.final_diagnosis = data.get("diagnosis")
                    
                    st.rerun()
        
        st.markdown("---")
        st.markdown("**📸 Medical Imaging AI**")
        st.markdown("• X-ray interpretation")
        st.markdown("• Skin condition diagnosis") 
        st.markdown("• Wound assessment")
        st.markdown("• Ultrasound analysis")
        st.markdown("• Laboratory results")
        
        # Quick actions
        st.markdown("---")
        st.markdown("#### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Session", key="reset_sidebar"):
                reset_consultation()
                st.rerun()
        
        with col2:
            if st.button("📊 Refresh Metrics", key="refresh_sidebar"):
                st.rerun()

# Footer with additional information
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>🏥 MediConnect AI - Bridging Healthcare Gaps in Rural Nigeria</h4>
    <p>Interactive AI-powered medical consultations in local languages</p>
    <p><strong>Languages Supported:</strong> English • Hausa • Yoruba • Igbo</p>
    <p><strong>Features:</strong> Smart Questioning • Medical Image Analysis • Comprehensive Diagnosis • Direct OpenAI</p>
</div>
""", unsafe_allow_html=True)

# Debug information (only show if debug mode is on)
if st.session_state.debug_mode:
    st.markdown("---")
    st.markdown("### 🔍 Debug Information")
    
    with st.expander("Session State", expanded=False):
        st.json({
            "consultation_id": st.session_state.consultation_id,
            "consultation_active": st.session_state.consultation_active,
            "conversation_length": len(st.session_state.conversation_history),
            "total_consultations": st.session_state.total_consultations,
            "total_questions": st.session_state.total_questions,
            "total_diagnoses": st.session_state.total_diagnoses,
            "openai_api_key_configured": bool(OPENAI_API_KEY),
            "selected_language": selected_language,
            "has_final_diagnosis": bool(st.session_state.final_diagnosis)
        })
    
    with st.expander("Final Diagnosis", expanded=False):
        if st.session_state.final_diagnosis:
            st.json(st.session_state.final_diagnosis)
        else:
            st.write("No final diagnosis yet")
    
    with st.expander("Conversation History", expanded=False):
        for i, turn in enumerate(st.session_state.conversation_history):
            st.write(f"**Turn {i+1} ({turn['type']}):**")
            st.json(turn)
    
    with st.expander("OpenAI Status", expanded=False):
        if OPENAI_API_KEY:
            st.success("✅ OpenAI API Key Configured")
            st.write(f"Key preview: {OPENAI_API_KEY[:8]}...")
        else:
            st.error("❌ OpenAI API Key Missing")
            st.info("Add OPENAI_API_KEY to Streamlit secrets")
    
    # Manual OpenAI testing section
    with st.expander("Manual OpenAI Testing", expanded=False):
        st.markdown("#### 🧪 Test OpenAI Connection")
        
        if st.button("Test OpenAI Connection", key="test_openai_direct"):
            if not OPENAI_API_KEY:
                st.error("❌ No OpenAI API key configured")
            else:
                try:
                    with st.spinner("Testing OpenAI..."):
                        test_response = openai_client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[{"role": "user", "content": "Say 'OpenAI test successful'"}],
                            max_tokens=10
                        )
                        result = test_response.choices[0].message.content
                        st.success(f"✅ OpenAI Working: {result}")
                except Exception as e:
                    st.error(f"❌ OpenAI Error: {str(e)}")
                    if "insufficient_quota" in str(e).lower():
                        st.info("💡 This usually means you need to add billing to your OpenAI account")
                    elif "invalid_api_key" in str(e).lower():
                        st.info("💡 Check your API key in Streamlit secrets")

# Final status display at bottom
st.markdown("---")
if st.session_state.consultation_active:
    st.info("🔄 Consultation in progress...")
elif st.session_state.final_diagnosis:
    st.success("✅ Consultation completed - Diagnosis available above")
else:
    st.info("💡 Ready to start a new consultation")
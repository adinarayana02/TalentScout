import streamlit as st
import uuid
from agent.conversation_handler import ConversationHandler
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO


@st.cache_resource
def get_custom_css():
    """Cache CSS to avoid recomputing on every rerun"""
    return """
        <style>
        /* Main container */
        .stApp {
            background-color: white
            color: black; /* White text color */
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #FFD700, #FFC107); /* Golden gradient */
            padding: 2rem;
            border-radius: 15px;
            color: black; /* White text */
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Chat container */
        .chat-message {
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            line-height: 1.5;
            position: relative;
            animation: fadeIn 0.3s ease-in;
        }

        .user-message {
            background-color: #000000; /* Black background */
            margin-left: 20%;
            margin-right: 1rem;
            border: 1px solid #FFD700; /* Golden border */
        }

        .assistant-message {
            background-color: #1C1C1C; /* Slightly lighter black for contrast */
            margin-right: 20%;
            margin-left: 1rem;
            border: 1px solid #FFC107; /* Golden border */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Progress indicators */
        .stage-indicator {
            padding: 0.75rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            text-align: center;
            transition: all 0.3s ease;
            color: #FFFFFF; /* White text */
        }

        .stage-active {
            background: linear-gradient(135deg, #FFD700, #FFC107); /* Golden gradient */
            color: #FFFFFF; /* White text */
            box-shadow: 0 2px 4px rgba(255, 215, 0, 0.3);
        }

        .stage-pending {
            background-color: #1C1C1C; /* Slightly lighter black */
            color: #757575; /* Gray text */
            border: 1px solid #FFD700; /* Golden border */
        }

        /* Input area */
        .input-container {
            background-color: #1C1C1C; /* Slightly lighter black */
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            color: #FFFFFF; /* White text */
        }

        .stTextInput > div > div > input {
            border-radius: 25px !important;
            padding: 0.75rem 1.5rem !important;
            border: 2px solid #FFD700 !important; /* Golden border */
            font-size: 1rem !important;
            color: #FFFFFF !important; /* White text */
            background-color: #000000 !important; /* Black background */
        }

        .stButton > button 
        {
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            background: linear-gradient(135deg, #FFD700, #FFC107); /* Golden gradient */
            color: #FFFFFF !important; /* White text */
            font-weight: 500 !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }


        stButton > button:hover 
        {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(255, 215, 0, 0.2) !important;
        }


        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Progress bar */
        .stProgress > div > div {
            background-color: #FFD700 !important; /* Golden progress bar */
        }

        .stProgress > div > div > div {
            background: linear-gradient(135deg, #FFD700, #FFC107) !important; /* Golden gradient */
        }

        /* Form styling */
        .form-container {
            background: #1C1C1C; /* Slightly lighter black */
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            color: #FFFFFF; /* White text */
        }

        /* Message formatting */
        .formatted-message {
            white-space: pre-line;
            line-height: 1.6;
            color: #FFFFFF; /* White text */
        }

        /* Technical questions styling */
        .question-card {
            background: #1C1C1C; /* Slightly lighter black */
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #FFD700; /* Golden accent */
            color: #FFFFFF; /* White text */
        }

        /* AI Evaluation Styling */
        .ai-evaluation {
            padding: 15px;
            background-color: #1C1C1C; /* Slightly lighter black */
            border-radius: 8px;
            margin: 10px 0;
            color: #FFFFFF; /* White text */
        }

        .evaluation-section h4,
        .evaluation-section p,
        .evaluation-section li {
            color: #FFFFFF; /* White text */
        }

        /* Loading animation */
        .loading-spinner::after {
            content: "";
            width: 40px;
            height: 40px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #FFD700; /* Golden spinner */
            border-radius: 50%;
            animation: spinner 1s linear infinite;
        }

        @keyframes spinner {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Pulse animation for processing text */
        .processing-text {
            animation: pulse 1.5s ease-in-out infinite;
            color: #FFFFFF; /* White text */
        }
        </style>
    """


def set_custom_css():
    st.markdown(get_custom_css(), unsafe_allow_html=True)

def format_message(message: str) -> str:
    """Format message text for better readability"""
    return message.replace('\\n', '\n').replace('\\t', '\t')

def handle_greeting():
    st.markdown("""
        
    """, unsafe_allow_html=True)
    return create_personal_info_form()

def handle_tech_stack(name: str):
    """Create and handle the technical skills form"""
    # Validate that we have personal info before proceeding
    if not hasattr(st.session_state, 'personal_info') or not st.session_state.personal_info:
        st.error("Please complete your personal information first.")
        if st.button("Return to Personal Information"):
            st.session_state.current_stage = 'greeting'
            st.rerun()
        return None, False

    st.markdown(f"""
      <div class="chat-message assistant-message" style="color: white;">
    <h3 style="color: white;">Technical Skills Assessment</h3>
    <p style="color: white;">Hi <strong>{name}</strong>, let's understand your technical expertise better.</p>
</div>

    """, unsafe_allow_html=True)
    return create_tech_stack_form()

def handle_technical_interview(skills: list):
    """Handle the technical interview stage with proper question management"""
    
    # Initialize technical interview session if not already done
    if 'tech_questions_initialized' not in st.session_state:
        try:
            # Generate questions based on skills
            questions = st.session_state.conversation_handler.generate_technical_questions(skills)
            if not questions or len(questions) == 0:
                st.error("Failed to generate technical questions. Please try again.")
                if st.button("Restart Interview"):
                    st.session_state.clear()
                    st.rerun()
                return
            
            st.session_state.tech_questions = questions
            st.session_state.current_question = 0
            st.session_state.tech_questions_initialized = True
            st.session_state.responses = []
            st.rerun()  # Rerun to refresh the page without the loading animation
            
        except Exception as e:
            st.error(f"Error initializing technical interview: {str(e)}")
            if st.button("Restart Interview"):
                st.session_state.clear()
                st.rerun()
            return

    # Display loading animation only during initial question generation
    if not st.session_state.get('tech_questions_initialized'):
        with st.spinner("🤖 AI is preparing your technical questions..."):
            st.markdown("""
                <div class="loading-spinner"></div>
                <p class="processing-text" style="text-align: center;">Analyzing your skills and generating relevant questions...</p>
            """, unsafe_allow_html=True)
            return

    # Safety check for questions
    if not hasattr(st.session_state, 'tech_questions') or not st.session_state.tech_questions:
        st.error("No technical questions available. Please restart the interview.")
        if st.button("Restart Interview"):
            st.session_state.clear()
            st.rerun()
        return

    current_q = st.session_state.current_question
    total_q = len(st.session_state.tech_questions)

    # Display progress
    st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <h3>Technical Interview</h3>
            <p>Question {current_q + 1} of {total_q}</p>
        </div>
    """, unsafe_allow_html=True)

    # Display current question
    try:
        current_question = st.session_state.tech_questions[current_q]
        st.markdown(f"""
            <div class="question-card">
                <p style="font-size: 1.1rem; font-weight: 500;">{current_question}</p>
            </div>
        """, unsafe_allow_html=True)

        # Answer input
        answer = st.text_area(
            "Your Answer",
            height=150,
            help="Provide a detailed explanation of your solution"
        )

        # Navigation buttons in three columns
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Previous", disabled=current_q == 0):
                st.session_state.current_question -= 1
                st.rerun()
        
        with col2:
            if st.button("Next", disabled=current_q == total_q - 1):
                st.session_state.current_question += 1
                st.rerun()

        with col3:
            submit_button = st.button(
                "Submit & Continue",
                type="primary",
                use_container_width=True,
                disabled=not answer
            )

        if submit_button and answer:
            with st.spinner(""):  # Empty spinner to prevent double spinners
                st.markdown("""
                    <div class="loading-spinner"></div>
                    <p class="processing-text" style="text-align: center;">AI is analyzing your response...</p>
                """, unsafe_allow_html=True)
                try:
                    response = st.session_state.conversation_handler.evaluate_answer(
                        current_question,
                        answer
                    )
                    
                    # Store response
                    if 'responses' not in st.session_state:
                        st.session_state.responses = []
                    
                    st.session_state.responses.append({
                        'question': current_question,
                        'answer': answer,
                        'evaluation': response
                    })
                    
                    # Show evaluation feedback
                    st.markdown("""
                        <div style="margin-top: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 10px;">
                            <h4 style="color: #1976d2;">Evaluation Feedback:</h4>
                    """, unsafe_allow_html=True)
                    st.write(response)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Progress to next question or complete
                    if current_q + 1 < total_q:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.current_stage = 'completed'
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error evaluating answer: {str(e)}")
                    return

    except IndexError:
        st.error("An error occurred accessing the current question. Resetting interview...")
        if st.button("Reset Interview"):
            st.session_state.clear()
            st.rerun()

def handle_completion():
    """Handle the completion stage with results summary and PDF download"""
    st.markdown("""
        <div class="chat-message assistant-message">
    <h3 style="color: white;">Technical Interview Completed! 🎉</h3>
    <p style="color: white;">Here's a comprehensive summary of your interview responses:</p>
    </div>
    """, unsafe_allow_html=True)

    if hasattr(st.session_state, 'responses') and st.session_state.responses:
        # Display responses
        for i, resp in enumerate(st.session_state.responses, 1):
            with st.expander(f"Question {i}", expanded=True):
                st.markdown(f"""
                    <div class="question-card">
                        <p style="font-size: 1.1rem; font-weight: 500;">{resp['question']}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="question-card">
                        <p><strong>Your Answer:</strong></p>
                        <p>{resp['answer']}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="question-card">
                        <p><strong>AI Evaluation:</strong></p>
                        {format_ai_response_html(resp['evaluation'])}
                    </div>
                """, unsafe_allow_html=True)
        
        # Generate and offer PDF download
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Generate PDF Summary", type="primary"):
                with st.spinner("Generating your comprehensive interview summary..."):
                    try:
                        # Create a dictionary with only the necessary data
                        summary_data = {
                            'personal_info': dict(st.session_state.personal_info) if hasattr(st.session_state, 'personal_info') else {},
                            'tech_stack': list(st.session_state.tech_stack) if hasattr(st.session_state, 'tech_stack') else [],
                            'responses': [
                                {
                                    'question': r['question'],
                                    'answer': r['answer'],
                                    'evaluation': r['evaluation']
                                } for r in st.session_state.responses
                            ]
                        }
                        pdf_buffer = generate_interview_summary(summary_data)
                        if pdf_buffer:
                            st.session_state.pdf_buffer = pdf_buffer
                            st.session_state.pdf_generated = True
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating PDF summary: {str(e)}")
        
        with col2:
            if hasattr(st.session_state, 'pdf_generated') and st.session_state.pdf_generated:
                st.download_button(
                    label="📥 Download Interview Summary",
                    data=st.session_state.pdf_buffer.getvalue(),
                    file_name="interview_summary.pdf",
                    mime="application/pdf",
                    key="download_pdf"
                )
    else:
        st.warning("No interview responses found. Please complete the interview first.")
        if st.button("Start New Interview"):
            st.session_state.clear()
            st.rerun()

@st.cache_data
def generate_interview_summary(data: dict):
    """Generate a PDF summary of the interview with proper error handling"""
    try:
        # Initialize PDF buffer
        buffer = BytesIO()
        
        # Set up the document with margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Initialize story and styles
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Technical Interview Summary", title_style))
        
        # Add personal information section
        if data.get('personal_info'):
            section_style = ParagraphStyle(
                'CustomSection',
                parent=styles['Heading2'],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=12
            )
            story.append(Paragraph("Personal Information", section_style))
            
            info = data['personal_info']
            table_data = [
                ["Full Name", info.get('full_name', 'N/A')],
                ["Email", info.get('email', 'N/A')],
                ["Phone", info.get('phone', 'N/A')],
                ["Experience", info.get('experience', 'N/A')],
                ["Position", info.get('desired_position', 'N/A')],
                ["Location", info.get('location', 'N/A')]
            ]
            
            table = Table(table_data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Add technical skills section
        if data.get('tech_stack'):
            story.append(Paragraph("Technical Skills", styles['Heading2']))
            skills_text = ", ".join(data['tech_stack'])
            story.append(Paragraph(skills_text, styles['Normal']))
            story.append(Spacer(1, 20))

        # Add interview responses section
        if data.get('responses'):
            story.append(Paragraph("Interview Questions and Evaluations", styles['Heading2']))

            for i, resp in enumerate(data['responses'], 1):
                # Question
                story.append(Paragraph(f"Question {i}:", styles['Heading3']))
                story.append(Paragraph(resp['question'], styles['Normal']))
                story.append(Spacer(1, 10))

                # Answer
                story.append(Paragraph("Your Answer:", styles['Heading4']))
                story.append(Paragraph(resp['answer'], styles['Normal']))
                story.append(Spacer(1, 10))

                # Evaluation
                story.append(Paragraph("AI Evaluation:", styles['Heading4']))
                story.append(Paragraph(resp['evaluation'], styles['Normal']))
                story.append(Spacer(1, 20))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def preprocess_ai_response(response: str) -> dict:
    """Cache AI response preprocessing"""
    sections = {
        'strengths': [],
        'areas_for_improvement': [],
        'overall_assessment': ''
    }

    try:
        # Remove ** markers and split into lines
        lines = response.replace('**', '').split('\n')

        current_section = None
        current_points = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Strengths:'):
                current_section = 'strengths'
                continue
            elif line.startswith('Areas for improvement:'):
                if current_points and current_section:
                    sections[current_section].extend(current_points)
                current_section = 'areas_for_improvement'
                current_points = []
                continue
            elif line.startswith('Overall assessment:'):
                if current_points and current_section:
                    sections[current_section].extend(current_points)
                current_section = 'overall_assessment'
                current_points = []
                continue

            # Process bullet points
            if line.startswith('* '):
                current_points.append(line[2:])
            else:
                if current_section == 'overall_assessment':
                    sections[current_section] = line
                else:
                    current_points.append(line)

        # Add any remaining points
        if current_points and current_section:
            if current_section == 'overall_assessment':
                sections[current_section] = ' '.join(current_points)
            else:
                sections[current_section].extend(current_points)

        return sections

    except Exception as e:
        st.error(f"Error processing AI response: {str(e)}")
        return {
            'strengths': [],
            'areas_for_improvement': [],
            'overall_assessment': response  # Return original response as overall assessment
        }

def format_ai_response_html(response: str) -> str:
    """Format AI response for HTML display"""
    sections = preprocess_ai_response(response)

    html = '<div class="ai-evaluation">'

    if sections['strengths']:
        html += '<div class="evaluation-section">'
        html += '<h4 style="color: #2e7d32;">Strengths:</h4>'
        html += '<ul>'
        for point in sections['strengths']:
            html += f'<li>{point}</li>'
        html += '</ul></div>'

    if sections['areas_for_improvement']:
        html += '<div class="evaluation-section">'
        html += '<h4 style="color: #c62828;">Areas for Improvement:</h4>'
        html += '<ul>'
        for point in sections['areas_for_improvement']:
            html += f'<li>{point}</li>'
        html += '</ul></div>'

    if sections['overall_assessment']:
        html += '<div class="evaluation-section">'
        html += '<h4 style="color: #1976d2;">Overall Assessment:</h4>'
        html += f'<p>{sections["overall_assessment"]}</p>'
        html += '</div>'

    html += '</div>'
    return html


def create_personal_info_form():
    """Create and handle the personal information form"""
    with st.form("personal_info_form"):
        st.markdown("""
            <div class="form-container">
                <h3 style='color: white; margin-bottom: 0.5rem;'>📋 Candidate Information</h3>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])  # Adjusted column widths

        # Define form fields
        with col1:
            st.markdown(
                "<label style='color: black;'>👤 Full Name*</label>",
                unsafe_allow_html=True
            )
            full_name = st.text_input("", key="name")

            st.markdown(
                "<label style='color: black;'>✉️ Email Address*</label>",
                unsafe_allow_html=True
            )
            email = st.text_input("", key="email")

            st.markdown(
                "<label style='color: black;'>📞 Phone Number*</label>",
                unsafe_allow_html=True
            )
            phone = st.text_input("", key="phone")

        with col2:
            st.markdown(
                "<label style='color: black;'>📅 Years of Experience*</label>",
                unsafe_allow_html=True
            )
            experience = st.text_input("", key="experience")

            st.markdown(
                "<label style='color: black;'>💼 Desired Position*</label>",
                unsafe_allow_html=True
            )
            position = st.text_input("", key="position")

            st.markdown(
                "<label style='color: black;'>📍 Current Location*</label>",
                unsafe_allow_html=True
            )
            location = st.text_input("", key="location")

        with col3:
            st.markdown(
                "<div style='text-align: center; color: black;'>📄 Upload Resume*</div>",
                unsafe_allow_html=True
            )

            resume = st.file_uploader("", type=["pdf", "doc", "docx"], key="resume")

        submit_button = st.form_submit_button(
            label="Submit Information",
            type="primary",
            use_container_width=True
        )

        if submit_button:
            # Check if all required fields are filled
            if all([full_name, email, phone, experience, position, location, resume]):
                return {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "experience": experience,
                    "desired_position": position,
                    "location": location,
                    "resume": resume
                }, True
            else:
                st.error("Please fill in all required fields.")
                return None, False
        return None, False


def create_tech_stack_form():
    """Create and handle the technical skills form"""
    with st.form("tech_stack_form"):
        st.markdown("""
            
        """, unsafe_allow_html=True)

        # Programming Languages - Split into 2 columns, 4 skills each
        languages = []
        st.markdown("### Programming Languages")
        col1, col2 = st.columns(2)

        with col1:
            if st.checkbox("Python"): languages.append("Python")
            if st.checkbox("JavaScript"): languages.append("JavaScript")
            if st.checkbox("Java"): languages.append("Java")
            if st.checkbox("C++"): languages.append("C++")

        with col2:
            if st.checkbox("C#"): languages.append("C#")
            if st.checkbox("Ruby"): languages.append("Ruby")
            if st.checkbox("PHP"): languages.append("PHP")
            if st.checkbox("Swift"): languages.append("Swift")

        # Frontend - Split into 2 columns, 4 skills each
        frontend = []
        st.markdown("### Frontend Technologies")
        col1, col2 = st.columns(2)

        with col1:
            if st.checkbox("React"): frontend.append("React")
            if st.checkbox("Angular"): frontend.append("Angular")
            if st.checkbox("Vue.js"): frontend.append("Vue.js")
            if st.checkbox("Svelte"): frontend.append("Svelte")

        with col2:
            if st.checkbox("HTML5"): frontend.append("HTML5")
            if st.checkbox("CSS3"): frontend.append("CSS3")
            if st.checkbox("SASS/SCSS"): frontend.append("SASS/SCSS")
            if st.checkbox("Webpack"): frontend.append("Webpack")

        # Backend - Split into 2 columns, 4 skills each
        backend = []
        st.markdown("### Backend Technologies")
        col1, col2 = st.columns(2)

        with col1:
            if st.checkbox("Node.js"): backend.append("Node.js")
            if st.checkbox("Django"): backend.append("Django")
            if st.checkbox("Flask"): backend.append("Flask")
            if st.checkbox("Spring Boot"): backend.append("Spring Boot")

        with col2:
            if st.checkbox("Laravel"): backend.append("Laravel")
            if st.checkbox("Express.js"): backend.append("Express.js")
            if st.checkbox("FastAPI"): backend.append("FastAPI")
            if st.checkbox("Ruby on Rails"): backend.append("Ruby on Rails")

        # Databases - Split into 2 columns, 4 skills each
        databases = []
        st.markdown("### Databases")
        col1, col2 = st.columns(2)

        with col1:
            if st.checkbox("PostgreSQL"): databases.append("PostgreSQL")
            if st.checkbox("MySQL"): databases.append("MySQL")
            if st.checkbox("MongoDB"): databases.append("MongoDB")
            if st.checkbox("Redis"): databases.append("Redis")

        with col2:
            if st.checkbox("SQLite"): databases.append("SQLite")
            if st.checkbox("Oracle"): databases.append("Oracle")
            if st.checkbox("Microsoft SQL Server"): databases.append("Microsoft SQL Server")
            if st.checkbox("Cassandra"): databases.append("Cassandra")

        # Cloud & DevOps - Split into 2 columns, 4 skills each
        cloud_devops = []
        st.markdown("### Cloud & DevOps")
        col1, col2 = st.columns(2)

        with col1:
            if st.checkbox("AWS"): cloud_devops.append("AWS")
            if st.checkbox("Azure"): cloud_devops.append("Azure")
            if st.checkbox("Google Cloud"): cloud_devops.append("Google Cloud")
            if st.checkbox("Docker"): cloud_devops.append("Docker")

        with col2:
            if st.checkbox("Kubernetes"): cloud_devops.append("Kubernetes")
            if st.checkbox("Jenkins"): cloud_devops.append("Jenkins")
            if st.checkbox("Git"): cloud_devops.append("Git")
            if st.checkbox("GitHub Actions"): cloud_devops.append("GitHub Actions")

        # Other Skills
        other_skills = st.text_area(
            "Other Skills (comma-separated)",
            placeholder="Enter any additional skills not listed above"
        )

        submit_button = st.form_submit_button(
            label="Submit Technical Skills",
            type="primary",
            use_container_width=True
        )

        if submit_button:
            all_skills = languages + frontend + backend + databases + cloud_devops
            if other_skills:
                additional_skills = [skill.strip() for skill in other_skills.split(',') if skill.strip()]
                all_skills.extend(additional_skills)

            if all_skills:
                return list(set(all_skills)), True  # Remove duplicates
            else:
                st.error("Please select at least one skill.")
                return None, False
        return None, False


def validate_form_data(form_data: dict, required_fields: list) -> tuple[bool, str]:
    """Centralized form validation"""
    missing_fields = [field for field in required_fields if not form_data.get(field)]
    if missing_fields:
        return False, f"Please fill in: {', '.join(missing_fields)}"
    return True, ""

def manage_session_state():
    """Centralized session state management"""
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'initialized': True,
            'current_stage': 'greeting',
            'session_id': str(uuid.uuid4()),
            'conversation_handler': ConversationHandler(),
            'tech_questions_initialized': False,
            'responses': [],
            'current_question': 0
        })

def safe_state_reset():
    """Safely reset application state"""
    keep_keys = ['initialized', 'session_id']
    preserved_values = {k: st.session_state[k] for k in keep_keys if k in st.session_state}
    st.session_state.clear()
    st.session_state.update(preserved_values)
    st.session_state.current_stage = 'greeting'

def handle_error(error: Exception, context: str):
    """Centralized error handling"""
    st.error(f"Error in {context}: {str(error)}")
    if st.button("Reset Application"):
        safe_state_reset()
        st.rerun()

def track_interview_progress():
    """Track and store interview progress metrics"""
    if 'metrics' not in st.session_state:
        st.session_state.metrics = {
            'start_time': time.time(),
            'questions_answered': 0,
            'total_time_spent': 0
        }
    
    if hasattr(st.session_state, 'responses'):
        st.session_state.metrics['questions_answered'] = len(st.session_state.responses)
        st.session_state.metrics['total_time_spent'] = time.time() - st.session_state.metrics['start_time']


def main():
    st.set_page_config(
        page_title="TalentScout AI Assistant",
        page_icon="👨‍💼",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    set_custom_css()

    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.clear()  # Clear any existing state
        st.session_state.initialized = True
        st.session_state.current_stage = 'greeting'
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.conversation_handler = ConversationHandler()

    # Header with Logo and Title
    st.markdown("""
        <div class="header" style="display: flex; align-items: center; justify-content: flex-start;">
            <img src="https://media.licdn.com/dms/image/sync/v2/D4E27AQGCiZMIlz11RQ/articleshare-shrink_800/articleshare-shrink_800/0/1726493729138?e=2147483647&v=beta&t=X4CjNTCk4wWBzv0k32n5T5a68PKapDMEIu6zJ833Eig" 
                 alt="TalentScout Logo" style="margin-right: 15px; height: 50px;"/>
            <div>
                <h1 style="margin: 0; color: white;">TalentScout AI Assistant</h1>
                <p style="color: white; margin: 0;">Your AI-powered technical interviewer</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Progress tracking
    stages = ['greeting', 'tech_stack', 'tech_questions', 'completed']
    stage_names = ['Personal Info', 'Technical Skills', 'Interview', 'Completed']
    current_index = stages.index(st.session_state.current_stage)


    # Stage indicators
    cols = st.columns(len(stages))
    for i, (stage, name) in enumerate(zip(stages, stage_names)):
        with cols[i]:
            if i < current_index:
                st.markdown(f"✅ {name}")
            elif i == current_index:
                st.markdown(f"🟡  {name}")
            else:
                st.markdown(f"⚪ {name}")

    # Main content
    if st.session_state.current_stage == 'greeting':
        info, submitted = handle_greeting()
        if submitted and info:
            st.session_state.personal_info = info
            st.session_state.current_stage = 'tech_stack'
            st.rerun()

    elif st.session_state.current_stage == 'tech_stack':
        # Validate personal info exists
        if not hasattr(st.session_state, 'personal_info') or not st.session_state.personal_info:
            st.error("Personal information is missing. Returning to the previous step.")
            st.session_state.current_stage = 'greeting'
            st.rerun()

        skills, submitted = handle_tech_stack(st.session_state.personal_info['full_name'])
        if submitted and skills:
            st.session_state.tech_stack = skills
            st.session_state.current_stage = 'tech_questions'
            st.rerun()

    elif st.session_state.current_stage == 'tech_questions':
        handle_technical_interview(st.session_state.tech_stack)

    elif st.session_state.current_stage == 'completed':
        handle_completion()

if __name__ == "__main__":
    main()
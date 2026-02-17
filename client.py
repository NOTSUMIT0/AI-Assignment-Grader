import streamlit as st
import requests
import json
import os
import tempfile
import time

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Assignment Grader",
    page_icon="📝",
    layout="wide"
)

# Sidebar - API Configuration (defined early to ensure keys are available)
with st.sidebar.expander("API Configuration", expanded=True):
    st.write("Configure your API keys here.")
    openai_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key", help="Required for grading and feedback.")
    google_key = st.text_input("Google API Key", type="password", key="google_api_key", help="Required for plagiarism check.")
    google_cx = st.text_input("Google Search Engine ID", type="password", key="google_cx", help="Required for plagiarism check.")
    
    if st.button("Save Settings"):
        st.success("Settings available for current session.")

# Function to call Server Core Functions directly
def call_tool_direct(tool_name, arguments):
    """Calls a core function from the server module directly."""
    try:
        # Set environment variables for the server tools to use
        if st.session_state.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = st.session_state.get("openai_api_key")
        if st.session_state.get("google_api_key"):
            os.environ["GOOGLE_API_KEY"] = st.session_state.get("google_api_key")
        if st.session_state.get("google_cx"):
            os.environ["GOOGLE_CX"] = st.session_state.get("google_cx")

        # Import server core functions
        from server import parse_file_core, check_plagiarism_core, grade_text_core, generate_feedback_core
        
        if tool_name == "parse_file":
            return parse_file_core(**arguments)
        elif tool_name == "check_plagiarism":
            return check_plagiarism_core(**arguments)
        elif tool_name == "grade_text":
            return grade_text_core(**arguments)
        elif tool_name == "generate_feedback":
            return generate_feedback_core(**arguments)
        else:
            return f"Error: Tool '{tool_name}' not found."

    except ImportError:
        return "Error: Could not import 'server.py'. Make sure it exists."
    except Exception as e:
        return f"Error calling tool '{tool_name}': {str(e)}"

# Main title
st.title("📝 Assignment Grader")
st.markdown("Upload assignments and grade them automatically with AI")

st.sidebar.header("About")
st.sidebar.info("""
This is a demo of the Assignment Grader using FastMCP and OpenAI.
Upload assignments in PDF or DOCX format, set your grading rubric,
and get instant AI-powered grades with detailed feedback.
""")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Upload Assignment", "Grade Assignment", "Results"])

# Tab 1: Upload Assignment
with tab1:
    st.header("Upload Assignment")

    # File Upload
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        st.session_state['file_path'] = file_path
        st.session_state['file_name'] = uploaded_file.name

        # Parse the document
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                result = call_tool_direct("parse_file", {"file_path": file_path})

                if result is None:
                    st.error("Failed to process document. Check server connection.")
                elif isinstance(result, str) and result.startswith("Error"):
                     st.error(result)
                elif isinstance(result, str):
                    # If result is a string, it's either the document text or an error message
                    st.session_state['document_text'] = result
                    st.success(f"Document processed successfully!")
                    st.info(f"Document contains {len(result.split())} words.")

                    # Show a preview
                    with st.expander("Document Preview"):
                        st.text(result[:1000] + ("..." if len(result) > 1000 else ""))
                else:        
                    # If result is a dict (unexpected for parse_file but possible if error dict)
                    st.session_state['document_text'] = str(result)
                    st.success(f"Document processed!")
                    st.json(result)

# Tab 2: Grade Assignment
with tab2:
    st.header("Grading Configuration")

    # Rubric input
    st.subheader("Grading Rubric")
    rubric = st.text_area(
        "Enter your grading rubric here:",
        height=200,
        help="Specify the criteria on which the assignment should be graded",
        value="""Content (40%): The assignment should demonstrate a through understanding of the topic.
Structure (20%): The assignment should be well-organized with a clear introduction, body, and conclusion.
Analysis (30%): The assignment should include critical analysis backed by evidence.
Grammar & Style (10%): The assignment should be free of grammatical errors and use appropriate academic tone."""
    )

    # Plagiarism check option
    check_plagiarism_option = st.checkbox("Check for plagiarism", value=True)

    if 'document_text' in st.session_state and st.button("Grade Assignment"):
        # Store rubric in session
        st.session_state['rubric'] = rubric
        
        # Validation
        if not st.session_state.get("openai_api_key"):
            st.error("Please enter your OpenAI API Key in the sidebar.")
        else:
            with st.spinner("Grading in progress..."):
                # Optional plagiarism check
                if check_plagiarism_option:
                    if not st.session_state.get("google_api_key") or not st.session_state.get("google_cx"):
                        st.warning("Skipping plagiarism check: Google API Key or Search Engine ID missing.")
                        st.session_state['plagiarism_results'] = None
                    else:
                        st.info("Checking for plagiarism...")
                        plagiarism_results = call_tool_direct("check_plagiarism", {"text": st.session_state['document_text']})
                        st.session_state['plagiarism_results'] = plagiarism_results
                        if plagiarism_results is None:
                            st.warning("Plagiarism check failed or returned no results.")

                # Generate grade
                st.info("Generating grade...")
                grade_results = call_tool_direct("grade_text", {
                    "text": st.session_state['document_text'],
                    "rubric": rubric
                })        
                st.session_state['grade_results'] = grade_results
                
                # Check for error in grade results
                if isinstance(grade_results, dict) and 'error' in grade_results:
                     st.error(f"Grading error: {grade_results['error']}")
                elif grade_results is None:
                    st.warning("Grade generation failed or returned no results.")

                # Generate feedback
                st.info("Generating feedback...")
                feedback = call_tool_direct("generate_feedback", {
                    "text": st.session_state['document_text'],
                    "rubric": rubric
                })    
                st.session_state['feedback'] = feedback
                
                if isinstance(feedback, str) and feedback.startswith("Error"):
                     st.error(feedback)
                elif feedback is None:
                    st.warning("Feedback generation failed or returned no results.")

                if (grade_results and 'error' not in grade_results) or (feedback and not feedback.startswith("Error")):
                    st.success("Grading completed!")
                    st.balloons()

    elif 'document_text' not in st.session_state:
        st.info("Please upload and process a document first in the 'Upload Assignment' tab.")

# Tab 3: Results
with tab3:
    st.header("Grading Results")

    if all(k in st.session_state for k in ['file_name']):
        st.subheader(f"Results for: {st.session_state['file_name']}")

        # Display grade
        if 'grade_results' in st.session_state and st.session_state['grade_results']:
            results = st.session_state['grade_results']
            if isinstance(results, dict) and 'error' not in results:
                grade = results.get('grade', 'Not available')
                score = results.get('score', '')
                st.metric("Grade", f"{grade} {score}")
                
                if 'breakdown' in results:
                    st.subheader("Breakdown")
                    st.json(results['breakdown'])
                
                if 'summary' in results:
                    st.info(results['summary'])
            elif isinstance(results, dict) and 'error' in results:
                 st.error(f"Grading Error: {results['error']}")

        # Display feedback
        if 'feedback' in st.session_state and st.session_state['feedback']:
            feedback = st.session_state['feedback']
            if not feedback.startswith("Error"):
                st.subheader("Feedback")  
                st.markdown(feedback)
            else:
                st.error(feedback)

        # Display plagiarism results if available
        if 'plagiarism_results' in st.session_state and st.session_state['plagiarism_results']:
            st.subheader("Plagiarism Check")
            results = st.session_state['plagiarism_results']   

            if 'error' in results:
                st.error(f"Plagiarism check error: {results['error']}")
            elif results:
                st.markdown("**Similarity matches found:**")
                if not results:
                    st.success("No significant plagiarism detected.")
                else:
                    for url, similarity in results.items():
                        if similarity > 70:
                            st.warning(f"High similarity ({similarity}%): [{url}]({url})")
                        elif similarity > 40:
                            st.success(f"Moderate similarity ({similarity}%): [{url}]({url})")
                        else: 
                            st.success(f"Low similarity ({similarity}%): [{url}]({url})")
            else:
                 st.info("No plagiarism detected or empty results.")

        # Export options
        st.subheader("Export Options")
        if st.button("Export to PDF"):
            st.info("PDF export functionality would go here")

        if st.button("Save to Database"):
            st.info("Database save functionality would go here")
    else:
        st.info("No grading results available. Please upload and grade an assignment first.")

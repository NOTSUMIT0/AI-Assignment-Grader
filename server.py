from fastmcp import FastMCP
import pymupdf
import docx
import os
import json
import requests
from fuzzywuzzy import fuzz
from openai import OpenAI
import google.generativeai as genai

# Initialize FastMCP server
mcp = FastMCP("Assignment Grader")

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# Core Logic Functions

def parse_file_core(file_path: str) -> str:
    """Parses a PDF or DOCX file and extracts text."""
    try:
        if file_path.endswith(".pdf"):
            doc = pymupdf.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        else:
            return "Error: Unsupported file format. Please upload PDF or DOCX."
    except Exception as e:
        return f"Error parsing file: {str(e)}"

def check_plagiarism_core(text: str) -> dict:
    """Checks for plagiarism using Google Search API and returns similarity scores."""
    try:
        # Use Google Custom Search API to find similar content
        # Note: This requires GOOGLE_API_KEY and GOOGLE_CX in environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CX")
        
        if not api_key or not cse_id:
            return {"error": "Google API configuration missing (GOOGLE_API_KEY or GOOGLE_CX)"}

        # Extract a snippet to search query (first 100 characters or key extraction)
        # Using a simple heuristic for now
        search_query = text[:100].replace("\n", " ") 
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': search_query
        }
        
        response = requests.get(url, params=params)
        results = response.json()
        
        similarity_scores = {}
        
        if 'items' in results:
            for item in results['items']:
                link = item.get('link')
                snippet = item.get('snippet', '')
                # Compare extracted text against snippet for a rough estimate
                similarity = fuzz.ratio(text[:500], snippet) 
                similarity_scores[link] = similarity
                
        return similarity_scores

    except Exception as e:
        return {"error": f"Plagiarism check failed: {str(e)}"}

def grade_text_core(text: str, rubric: str) -> dict:
    """Grades the text based on the provided rubric using OpenAI."""
    try:
        client = get_openai_client()
        if not client:
             return {"error": "OpenAI API key missing"}

        prompt = f"""
        You are an AI grader. Grade the following assignment based on the rubric provided.
        
        Rubric:
        {rubric}
        
        Assignment:
        {text}
        
        Return the response in valid JSON format with the following structure:
        {{
            "grade": "Letter Grade (e.g., A, B+)",
            "score": "Numeric Score (e.g., 85/100)",
            "breakdown": {{
                "criteria_name": "score/max"
            }},
            "summary": "Brief summary of the grading"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that grades assignments. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        return result
        
    except Exception as e:
        # Check if the error is related to quota
        if "quota" in str(e).lower():
             return {"error": "OpenAI API quota exceeded. Please check your billing details."}
        return {"error": f"Grading failed: {str(e)}"}

def generate_feedback_core(text: str, rubric: str) -> str:
    """Generates detailed feedback for the assignment using OpenAI."""
    try:
        client = get_openai_client()
        if not client:
             return "Error: OpenAI API key missing"

        prompt = f"""
        Provide detailed, constructive feedback for this assignment based on the rubric.
        
        Rubric:
        {rubric}
        
        Assignment:
        {text}
        
        Format the output in Markdown.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides educational feedback."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        if "quota" in str(e).lower():
             return "Error: OpenAI API quota exceeded. Please check your billing details."
        return f"Feedback generation failed: {str(e)}"

# MCP Tools Wrappers

@mcp.tool()
def parse_file(file_path: str) -> str:
    """Parses a PDF or DOCX file and extracts text."""
    return parse_file_core(file_path)

@mcp.tool()
def check_plagiarism(text: str) -> dict:
    """Checks for plagiarism using Google Search API and returns similarity scores."""
    return check_plagiarism_core(text)

@mcp.tool()
def grade_text(text: str, rubric: str) -> dict:
    """Grades the text based on the provided rubric using OpenAI."""
    return grade_text_core(text, rubric)

@mcp.tool()
def generate_feedback(text: str, rubric: str) -> str:
    """Generates detailed feedback for the assignment using OpenAI."""
    return generate_feedback_core(text, rubric)

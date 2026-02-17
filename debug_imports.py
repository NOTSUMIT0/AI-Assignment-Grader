try:
    print("Importing pymupdf...")
    import pymupdf
    print("✅ pymupdf imported")
except Exception as e:
    print(f"❌ pymupdf failed: {e}")

try:
    print("Importing docx...")
    import docx
    print("✅ docx imported")
except Exception as e:
    print(f"❌ docx failed: {e}")

try:
    print("Importing fuzzywuzzy...")
    from fuzzywuzzy import fuzz
    print("✅ fuzzywuzzy imported")
except Exception as e:
    print(f"❌ fuzzywuzzy failed: {e}")

try:
    print("Importing openai...")
    from openai import OpenAI
    print("✅ openai imported")
except Exception as e:
    print(f"❌ openai failed: {e}")

try:
    print("Importing google.generativeai...")
    import google.generativeai as genai
    print("✅ google.generativeai imported")
except Exception as e:
    print(f"❌ google.generativeai failed: {e}")

try:
    print("Importing fastmcp...")
    from fastmcp import FastMCP
    print("✅ fastmcp imported")
except Exception as e:
    print(f"❌ fastmcp failed: {e}")

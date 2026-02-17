
print("Verifying imports...")
try:
    from server import parse_file_core, check_plagiarism_core, grade_text_core, generate_feedback_core
    print("✅ Server core functions imported successfully.")
except Exception as e:
    print(f"❌ Error importing server functions: {e}")
    exit(1)

print("Setup verification passed.")

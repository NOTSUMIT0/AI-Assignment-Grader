
try:
    from server import parse_file, check_plagiarism, grade_text, generate_feedback
    print("Successfully imported functions from server")
    
    # Test parse_file with a dummy path
    # We expect it to fail with file not found or return error string, but not crash on call
    print(f"Type of parse_file: {type(parse_file)}")
    
    # Check if they are coroutines or regular functions
    import inspect
    if inspect.iscoroutinefunction(parse_file):
        print("parse_file is a coroutine function")
    else:
        print("parse_file is a regular function")

    try:
        # Create a dummy file to test parsing
        with open("test_dummy.txt", "w") as f:
            f.write("Hello World")
            
        # parse_file expects pdf or docx, so it should return error string
        result = parse_file("test_dummy.txt")
        print(f"Result of calling parse_file: {result}")
        
    except Exception as e:
        print(f"Error calling parse_file: {e}")

except ImportError as e:
    print(f"Failed to import functions: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

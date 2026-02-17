
try:
    from server import parse_file
    print(f"Type of parse_file: {type(parse_file)}")
    print(f"Dir of parse_file: {dir(parse_file)}")
    
    if hasattr(parse_file, 'run'):
        print(f"parse_file.run is {parse_file.run}")
        import inspect
        if inspect.iscoroutinefunction(parse_file.run):
             print("parse_file.run is async")
        else:
             print("parse_file.run is sync")

    if hasattr(parse_file, 'fn'):
        print(f"parse_file.fn is {parse_file.fn}")
        # Try calling the underlying function if accessible
        # parse_file.fn("test_dummy.txt") 

except ImportError as e:
    print(f"Failed to import parse_file: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

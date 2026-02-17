
try:
    from server import mcp
    print("Successfully imported mcp from server")
    print(f"MCP Object: {mcp}")
    
    try:
        tool = mcp.get_tool("parse_file")
        print(f"Got tool 'parse_file': {tool}")
        if tool:
            print("Tool found. Attempting to run (mock)...")
            # We won't run it with a real file here, just checking existence and type
            if hasattr(tool, 'run'):
                 print("Tool has 'run' method.")
            else:
                 print("Tool does NOT have 'run' method.")
                 print(f"Tool dir: {dir(tool)}")
        else:
            print("Tool 'parse_file' returned None.")

    except AttributeError:
        print("mcp.get_tool does not exist.")
        print(f"MCP dir: {dir(mcp)}")

except ImportError as e:
    print(f"Failed to import server: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

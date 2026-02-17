try:
    import server
    print("✅ server.py imported successfully")
except ImportError as e:
    print(f"❌ server.py import failed: {e}")
except Exception as e:
    print(f"❌ server.py error: {e}")

try:
    # client.py is a script, not a module, but we can check for syntax errors by compiling it
    with open("client.py", "r", encoding="utf-8") as f:
        compile(f.read(), "client.py", "exec")
    print("✅ client.py syntax is valid")
except Exception as e:
    print(f"❌ client.py syntax error: {e}")

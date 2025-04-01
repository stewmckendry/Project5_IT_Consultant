import os

def find_openai_calls(match_text="call_openai_with_tracking("):
    matches = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("Searching in directory:", root_dir)
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(foldername, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, start=1):
                        if match_text in line:
                            matches.append((filepath, i, line.strip()))

    return matches

# Run it if this file is executed directly
if __name__ == "__main__":
    results = find_openai_calls()
    for path, lineno, code in results:
        print(f"{path}:{lineno} ➜ {code}")
    if not results:
        print("No matches found.")

def extract_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join([chunk.get("text", "") for chunk in content if isinstance(chunk, dict) and "text" in chunk])
    return str(content)

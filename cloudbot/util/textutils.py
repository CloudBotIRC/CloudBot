"text.py - text formatting utilities"

def truncate(text, limit=75, suffix='...'):
    text = text.split('\n')[0]
    
    return ' '.join(text[:limit+1].split(' ')[0:-1]) + suffix
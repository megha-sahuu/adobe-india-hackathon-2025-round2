from datetime import datetime

def get_processing_timestamp():
    return datetime.now().isoformat() 
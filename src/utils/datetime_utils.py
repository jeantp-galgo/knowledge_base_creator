from datetime import datetime

def get_current_date_format_yyyy_mm_dd() -> str:
    """
    Obtiene la fecha actual en formato YYYY-MM-DD
    """
    return datetime.now().strftime("%Y-%m-%d")
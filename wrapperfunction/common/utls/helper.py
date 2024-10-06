import re
def process_text_name(txt):
    # Remove URL components
    individual_filename = txt.replace("https://", '').replace("www.", '').replace(".com", '')
    
    # Replace special characters with underscores
    individual_filename = re.sub(r'[?+.=\-\\\/|%]', '_', individual_filename)
    
    # Truncate if the filename is too long
    if len(individual_filename) >= 40:
        individual_filename = individual_filename[:25] + individual_filename[-30:]
    
    return individual_filename
import pandas as pd
# df_prev = pd.read_csv('./data/mimic-iv/pre_line_info_raw.csv') # adjust the path as needed
df_prev = pd.read_csv('../../../data/mimic-iv/pre_line_info_raw.csv')
pre_treatment_keywords = [
    'treatment history', 'prior', 'previous', 'prev ',
    'line of therapy', 'first line', 'second line', 'third line'
]
# Function to find notes containing pre-treatment information
def find_pre_treatment_info(note_content):
    if pd.isna(note_content):
        return False
    
    # Convert to lowercase for case-insensitive matching
    content_lower = str(note_content).lower()
    
    # Check if any keyword is present
    for keyword in pre_treatment_keywords:
        if keyword.lower() in content_lower:
            return True
    
    return False

# Apply the function to filter rows with pre-treatment information
df_prev['has_pre_treatment_info'] = df_prev['note_content'].apply(find_pre_treatment_info)
import re
import pandas as pd

def highlight_pre_treatment_info(note_content):
    """
    Find out and hightlight the keyword in note_content(suitable for VS Code/terminal）
    """
    if pd.isna(note_content):
        return

    text = str(note_content)
    text_lower = text.lower()

    pattern = r'(' + '|'.join([re.escape(k.lower()) for k in pre_treatment_keywords]) + r')'

    # find all the keywords
    matches = list(re.finditer(pattern, text_lower, flags=re.IGNORECASE))

    if not matches:
        return

    # print the matched keyword and position
    print(f"\n{'='*80}")
    print(" Found keywords:")
    for m in matches:
        keyword = text[m.start():m.end()]
        print(f" - '{keyword}' at position [{m.start()}:{m.end()}]")

    # insert ANSI yellow color highlight in the text
    highlighted_text = ""
    last_end = 0
    for m in matches:
        start, end = m.span()
        # concat the raw text + highlight text
        highlighted_text += text[last_end:start]
        highlighted_text += f"\033[93m{text[start:end]}\033[0m"  # yellow color highlight part
        last_end = end
    highlighted_text += text[last_end:]  # add the last part

    print("\n Highlighted text:\n")
    print(highlighted_text)
    print("="*80)

df_prev['note_content'].apply(highlight_pre_treatment_info)

patients_with_info = df_prev[df_prev['has_pre_treatment_info']]['subject_id'].nunique()
print(f"Number of unique patients with pre-treatment information: {patients_with_info}")
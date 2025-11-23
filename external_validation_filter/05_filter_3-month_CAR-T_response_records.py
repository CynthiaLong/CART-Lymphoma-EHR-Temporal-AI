import pandas as pd
import re
from datetime import datetime

df_eval = pd.read_csv('./data/mimic-iv/3_month_eval_raw.csv') # revises the path as needed

efficacy_terms = [
    'CR', 'PR', 'PD', 'SD',
    'Complete Response', 'Partial Response', 
    'Stable Disease', 'Progressive Disease'
]
# Improved function with highlighting of found terms
def extract_efficacy_sentences_highlighted(note_content):
    if pd.isna(note_content):
        return []
    
    efficacy_sentences = []
    
    # Split text into sentences (using ., !, ? as delimiters)
    sentences = re.split(r'[.!?]+', str(note_content))
    
    for sentence in sentences:
        sentence_clean = sentence.strip()
        if not sentence_clean:
            continue
            
        # Check for matches with precise word boundary matching
        found_terms = []
        
        # For single letter terms (CR, PR, PD, SD), use word boundaries
        single_term_matches = re.finditer(r'\b(CR|PR|PD|SD)\b', sentence_clean, re.IGNORECASE)
        for match in single_term_matches:
            found_terms.append((match.start(), match.end(), match.group()))
            
        # For multi-word terms, also check with word boundaries
        multi_term_matches = re.finditer(r'\b(Complete\s+Response|Partial\s+Response|Stable\s+Disease|Progressive\s+Disease)\b', 
                                        sentence_clean, re.IGNORECASE)
        for match in multi_term_matches:
            found_terms.append((match.start(), match.end(), match.group()))
            
        # If we found any terms, highlight them and add to results
        if found_terms:
            # print(found_terms)
            # Sort by position in sentence
            found_terms.sort(key=lambda x: x[0])
            
            # Create highlighted version of sentence
            highlighted_sentence = ""
            last_pos = 0
            
            for start, end, term in found_terms:
                # Add text before the match
                highlighted_sentence += sentence_clean[last_pos:start]
                # Add highlighted match
                highlighted_sentence += f"**[{term.upper()}]**"
                last_pos = end
            
            # Add remaining text
            highlighted_sentence += sentence_clean[last_pos:]
            
            # Print the original sentence and highlighted version
            # print(f"Original: {sentence_clean}")
            # print(f"Highlighted: {highlighted_sentence}")
            # print("=" * 50)
            
            efficacy_sentences.append({
                # 'sentence': sentence_clean,
                'highlighted': highlighted_sentence,
                'terms_found': [term for _, _, term in found_terms]
            })
    # if efficacy_sentences:
    #         print(1)    
    return efficacy_sentences

# Apply the improved function with highlighting
df_eval['efficacy_sentences_highlighted'] = df_eval['note_content'].apply(extract_efficacy_sentences_highlighted)

# Add a column to calculate the time difference in days between note_time and car_t_procedure_date
def calculate_days_difference(row):
    # Convert note_time to datetime (includes time component)
    note_time = pd.to_datetime(row['note_time'])
    
    # Convert car_t_procedure_date to datetime (date only)
    procedure_date = pd.to_datetime(row['car_t_procedure_date'])
    
    # Calculate the difference in days
    days_diff = (note_time - procedure_date).days
    
    return days_diff

# Apply the function to create the new column
df_eval['days_after_car_t'] = df_eval.apply(calculate_days_difference, axis=1)
# Count records with non-empty efficacy sentences and days_after_car_t >= 90
filtered_count = df_eval[
    (df_eval['efficacy_sentences_highlighted'].apply(len) > 0) & 
    (df_eval['days_after_car_t'] >= 90)
].shape[0]

# Display the result
print(f"Number of hospital records with efficacy information and days_after_car_t >= 90: {filtered_count}")

# If you want to see the actual records, you can use:
filtered_records = df_eval[
    (df_eval['efficacy_sentences_highlighted'].apply(len) > 0) & 
    (df_eval['days_after_car_t'] >= 90)
]

print(f"\nDetails of these {filtered_count} records:")
print(filtered_records[['subject_id', 'hadm_id', 'car_t_procedure_date', 'note_time', 'days_after_car_t']])

import pandas as pd
import random
import csv
from pathlib import Path

raw_path = Path('data/raw/all_issues.csv')
data_dir = Path('data')
seed = 123
n = 250
pilot_pct = 0.12

print(f"Reading {raw_path}...")
df = pd.read_csv(raw_path)
all_processed = df.to_dict('records')

random.seed(seed)
if len(all_processed) > n:
    sample = random.sample(all_processed, n)
else:
    sample = all_processed

pilot_size = max(1, int(len(sample) * pilot_pct))
random.seed(seed)
pilot_indices = set(random.sample(range(len(sample)), pilot_size))

pilot_issues = []
for i, issue in enumerate(sample):
    if i in pilot_indices:
        issue['selected_for_pilot'] = 'TRUE'
        issue['notes'] = ''
        pilot_issues.append(issue)

pilot_df = pd.DataFrame(pilot_issues)
pilot_df = pilot_df.sort_values(['repo', 'issue_id']).reset_index(drop=True)

pilot_path = data_dir / 'pilot_sample_new.csv'
pilot_df.to_csv(pilot_path, index=False, quoting=csv.QUOTE_ALL)
print(f"Saved new pilot sample: {pilot_path} ({len(pilot_df)} rows) with seed {seed}")

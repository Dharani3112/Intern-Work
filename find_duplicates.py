import re

# Read the file content
with open('add_sample_books.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all book titles using regex
title_pattern = r"'title':\s*'([^']+)'"
titles = re.findall(title_pattern, content)

print(f"Total books found: {len(titles)}")

# Check for duplicates
title_dict = {}
duplicates = []

for i, title in enumerate(titles):
    if title in title_dict:
        duplicates.append((i, title, title_dict[title]))
        print(f"DUPLICATE FOUND: '{title}' appears at positions {title_dict[title] + 1} and {i + 1}")
    else:
        title_dict[title] = i

print(f"\nSummary:")
print(f"Total titles: {len(titles)}")
print(f"Unique titles: {len(title_dict)}")
print(f"Duplicates: {len(duplicates)}")

if duplicates:
    print(f"\nWe need to replace {len(duplicates)} duplicate books.")
else:
    print("No duplicates found!")

from add_sample_books import sample_books

# Check for duplicate ISBNs
isbn_dict = {}
duplicates = []

for i, book in enumerate(sample_books):
    isbn = book['isbn']
    if isbn in isbn_dict:
        duplicates.append((i, book['title'], isbn_dict[isbn], sample_books[isbn_dict[isbn]]['title']))
    else:
        isbn_dict[isbn] = i

print(f"Total books: {len(sample_books)}")
print(f"Duplicate ISBNs found: {len(duplicates)}")

if duplicates:
    print("\nDuplicate ISBNs:")
    for book_idx, book_title, orig_idx, orig_title in duplicates:
        print(f"Book {book_idx + 1}: '{book_title}' has same ISBN as Book {orig_idx + 1}: '{orig_title}'")
        print(f"ISBN: {sample_books[book_idx]['isbn']}")
        print()
else:
    print("No duplicate ISBNs found!")

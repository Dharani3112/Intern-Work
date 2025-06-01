from add_sample_books import sample_books

print(f"Total books in collection: {len(sample_books)}")
print(f"We need {100 - len(sample_books)} more books to reach 100")

# List the last few books to see where we are
print("\nLast 5 books in the collection:")
for i, book in enumerate(sample_books[-5:], len(sample_books)-4):
    print(f"{i}. {book['title']} by {book['author']}")

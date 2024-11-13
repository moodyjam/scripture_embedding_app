import csv
import re

# Initialize variables
book = ''
chapter = ''
current_verse_number = ''
current_verse_text = ''
data = []

# Regular expressions to match chapter headings and verses
chapter_pattern = re.compile(r'^([\dA-Za-z\s]+)\s+Chapter\s+(\d+)$')
verse_pattern = re.compile(r'^(\d+):(\d+)\s+(.*)$')

# Books with only one chapter
single_chapter_books = {'Enos', 'Jarom', 'Omni', 'Words of Mormon'}

with open('book_of_mormon.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

collecting_verse = False

for line in lines:
    line = line.strip()

    # Stop processing if we reach the Project Gutenberg footer
    if line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
        break

    # Skip empty lines
    if not line:
        continue

    # Detect chapter headings (e.g., "1 Nephi Chapter 2" or "Alma 5")
    chapter_match = chapter_pattern.match(line)
    if chapter_match:
        # Save any previous verse
        if collecting_verse:
            data.append([book, chapter, current_verse_number, current_verse_text.strip()])
            current_verse_text = ''
            collecting_verse = False

        # Update book and chapter
        book_chapter_text = chapter_match.group(1).strip()
        chapter_number = chapter_match.group(2).strip()

        # Split the book and chapter number in the book name
        # For cases like "1 Nephi" or "Alma"
        book_parts = book_chapter_text.split()
        if len(book_parts) > 1 and book_parts[-1].isdigit():
            book = ' '.join(book_parts[:-1])
            chapter = book_parts[-1]
        else:
            book = book_chapter_text
            chapter = chapter_number
        continue

    # Handle single-chapter books (e.g., "Enos", "Jarom", "Omni", "Words of Mormon")
    if line in single_chapter_books:
        # Save any previous verse
        if collecting_verse:
            data.append([book, chapter, current_verse_number, current_verse_text.strip()])
            current_verse_text = ''
            collecting_verse = False

        # Set book name and chapter to "1" (since it's a single-chapter book)
        book = line
        chapter = '1'
        continue

    # Detect verses (e.g., "1:1 I, Nephi, ...")
    verse_match = verse_pattern.match(line)
    if verse_match:
        # Save the previous verse
        if collecting_verse:
            data.append([book, chapter, current_verse_number, current_verse_text.strip()])
            current_verse_text = ''
        
        # Start a new verse
        current_verse_number = verse_match.group(2)
        current_verse_text = verse_match.group(3).strip()
        collecting_verse = True
    else:
        # Append line to current verse if we're collecting one
        if collecting_verse:
            current_verse_text += ' ' + line.strip()
        else:
            # Ignore other lines
            continue

# After the loop, save any remaining verse
if collecting_verse:
    data.append([book, chapter, current_verse_number, current_verse_text.strip()])

# Write data to CSV
with open('book_of_mormon.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Book', 'Chapter', 'Verse Number', 'Verse Text'])
    writer.writerows(data)

print("Data has been successfully written to book_of_mormon.csv")
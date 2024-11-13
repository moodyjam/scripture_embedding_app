import csv
import re

# Simplify book names
book_mappings = {
    # Old Testament
    'The First Book of Moses: Called Genesis': 'Genesis',
    'The Second Book of Moses: Called Exodus': 'Exodus',
    'The Third Book of Moses: Called Leviticus': 'Leviticus',
    'The Fourth Book of Moses: Called Numbers': 'Numbers',
    'The Fifth Book of Moses: Called Deuteronomy': 'Deuteronomy',
    'The Book of Joshua': 'Joshua',
    'The Book of Judges': 'Judges',
    'The Book of Ruth': 'Ruth',
    'The First Book of Samuel': '1 Samuel',
    'The Second Book of Samuel': '2 Samuel',
    'The First Book of the Kings': '1 Kings',
    'The Second Book of the Kings': '2 Kings',
    'The First Book of the Chronicles': '1 Chronicles',
    'The Second Book of the Chronicles': '2 Chronicles',
    'Ezra': 'Ezra',
    'The Book of Nehemiah': 'Nehemiah',
    'The Book of Esther': 'Esther',
    'The Book of Job': 'Job',
    'The Book of Psalms': 'Psalms',
    'The Proverbs': 'Proverbs',
    'Ecclesiastes': 'Ecclesiastes',
    'The Song of Solomon': 'Song of Solomon',
    'The Book of the Prophet Isaiah': 'Isaiah',
    'The Book of the Prophet Jeremiah': 'Jeremiah',
    'The Lamentations of Jeremiah': 'Lamentations',
    'The Book of the Prophet Ezekiel': 'Ezekiel',
    'The Book of Daniel': 'Daniel',
    'Hosea': 'Hosea',
    'Joel': 'Joel',
    'Amos': 'Amos',
    'Obadiah': 'Obadiah',
    'Jonah': 'Jonah',
    'Micah': 'Micah',
    'Nahum': 'Nahum',
    'Habakkuk': 'Habakkuk',
    'Zephaniah': 'Zephaniah',
    'Haggai': 'Haggai',
    'Zechariah': 'Zechariah',
    'Malachi': 'Malachi',
    # New Testament
    'The Gospel According to Saint Matthew': 'Matthew',
    'The Gospel According to Saint Mark': 'Mark',
    'The Gospel According to Saint Luke': 'Luke',
    'The Gospel According to Saint John': 'John',
    'The Acts of the Apostles': 'Acts',
    'The Epistle of Paul the Apostle to the Romans': 'Romans',
    'The First Epistle of Paul the Apostle to the Corinthians': '1 Corinthians',
    'The Second Epistle of Paul the Apostle to the Corinthians': '2 Corinthians',
    'The Epistle of Paul the Apostle to the Galatians': 'Galatians',
    'The Epistle of Paul the Apostle to the Ephesians': 'Ephesians',
    'The Epistle of Paul the Apostle to the Philippians': 'Philippians',
    'The Epistle of Paul the Apostle to the Colossians': 'Colossians',
    'The First Epistle of Paul the Apostle to the Thessalonians': '1 Thessalonians',
    'The Second Epistle of Paul the Apostle to the Thessalonians': '2 Thessalonians',
    'The First Epistle of Paul the Apostle to Timothy': '1 Timothy',
    'The Second Epistle of Paul the Apostle to Timothy': '2 Timothy',
    'The Epistle of Paul the Apostle to Titus': 'Titus',
    'The Epistle of Paul the Apostle to Philemon': 'Philemon',
    'The Epistle of Paul the Apostle to the Hebrews': 'Hebrews',
    'The General Epistle of James': 'James',
    'The First Epistle General of Peter': '1 Peter',
    'The Second General Epistle of Peter': '2 Peter',
    'The First Epistle General of John': '1 John',
    'The Second Epistle General of John': '2 John',
    'The Third Epistle General of John': '3 John',
    'The General Epistle of Jude': 'Jude',
    'The Revelation of Saint John the Divine': 'Revelation',
}

# Read the entire text into a single string
with open('bible.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Split the text into Old and New Testament
testament_split = re.split(r'The New Testament of the King James Bible', text)

if len(testament_split) == 2:
    old_testament_text = testament_split[0]
    new_testament_text = testament_split[1]
else:
    print("Could not find the New Testament delimiter in text.")
    exit(1)

def process_testament(testament_text):
    # Initialize variables
    testament_lines = []
    book_texts = {}  # Dictionary to hold text per book
    current_book = ''
    current_text = ''
    
    # Split the testament text into lines
    lines = testament_text.splitlines()
    
    for line in lines:
        line = line.strip()
        # Check for book names
        if line in book_mappings:
            # If there is a current book, save its text
            if current_book:
                book_texts[current_book] = current_text
                current_text = ''
            current_book = book_mappings[line]
            continue
        # Skip empty lines and headers
        if not line or line.startswith("***"):
            continue
        # Append line to current text
        current_text += line + ' '
    
    # After the loop, don't forget to save the last book's text
    if current_book:
        book_texts[current_book] = current_text
    
    # Now, process each book individually
    verse_pattern = re.compile(r'(\d+):(\d+)\s+(.*?)(?=(\d+:\d+\s+)|$)', re.DOTALL)
    
    for book, text in book_texts.items():
        for match in verse_pattern.finditer(text):
            chapter = match.group(1)
            verse_number = match.group(2)
            verse_text = match.group(3).strip()
            testament_lines.append([book, chapter, verse_number, verse_text])
    
    return testament_lines

# Process Old Testament
old_testament_lines = process_testament(old_testament_text)

# Process New Testament
new_testament_lines = process_testament(new_testament_text)

# Write Old Testament data to CSV
with open('old_testament.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Book', 'Chapter', 'Verse Number', 'Verse Text'])
    writer.writerows(old_testament_lines)

# Write New Testament data to CSV
with open('new_testament.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Book', 'Chapter', 'Verse Number', 'Verse Text'])
    writer.writerows(new_testament_lines)

print("Data has been successfully written to new_testament.csv and old_testament.csv")
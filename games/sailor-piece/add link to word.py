import os
import re
from bs4 import BeautifulSoup

def process_html_files():
    # 1. Get input from the user
    target_word = input("Enter the word you want to turn into a link: ").strip()
    target_url = input("Enter the URL to redirect to (e.g., https://google.com): ").strip()

    if not target_word or not target_url:
        print("Error: Word and URL cannot be empty.")
        return

    # 2. Find all HTML files in the current folder
    html_files = [f for f in os.listdir('.') if f.endswith(('.html', '.htm'))]

    if not html_files:
        print("No HTML files found in the current directory.")
        return

    print(f"\nFound {len(html_files)} HTML file(s). Processing...")

    # Compile a regex pattern to find whole words only, ignoring case
    pattern = re.compile(rf'\b({re.escape(target_word)})\b', re.IGNORECASE)

    # Define the custom CSS style for the link (Dark Gold + Dotted Underline)
    link_style = "color: #b8860b; text-decoration: underline dotted;"

    # 3. Loop through and update each file
    for filename in html_files:
        try:
            # Read the file
            with open(filename, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            modified = False

            # Search only through the text content of the HTML
            for text_node in soup.find_all(string=pattern):
                
                # Skip text if it's already inside an anchor <a> tag
                if text_node.parent.name == 'a':
                    continue
                # Skip text inside scripts, stylesheets, or page titles
                if text_node.parent.name in ['script', 'style', 'title']:
                    continue

                # Replace the word with the anchor tag AND the custom style
                new_html_string = pattern.sub(rf'<a href="{target_url}" style="{link_style}">\1</a>', text_node)

                # Parse the newly created HTML string and replace the old text node
                new_soup = BeautifulSoup(new_html_string, 'html.parser')
                text_node.replace_with(new_soup)
                modified = True

            # 4. Save the file if changes were made
            if modified:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(str(soup))
                print(f"✅ Updated: {filename}")
            else:
                print(f"➖ No changes needed: {filename}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    process_html_files()

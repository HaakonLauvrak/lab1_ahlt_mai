def process_file(input_filename):
    # Dictionary to store words by category
    categories = {
        'brand': [],
        'drug': [],
        'drug_n': [],
        'group': []
    }
    
    # Read the input file
    with open(input_filename, 'r', encoding='utf-8') as file:
        for line in file:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Split the line by '|'
            parts = line.strip().split('|')
            
            # Check if the line has the expected format
            if len(parts) >= 4:
                word = parts[2]  # The third part (index 2) is the word
                category = parts[3]  # The fourth part (index 3) is the category
                
                # Add the word to the appropriate category list
                if category in categories:
                    categories[category].extend(word.split(" "))
                else:
                    print(f"Warning: Unknown category '{category}' for word '{word}'")
    
    # Write each category to its corresponding output file
    for category, words in categories.items():
        output_filename = f"{category}.txt"
        with open(output_filename, 'w', encoding='utf-8') as file:
            for word in words:
                file.write(f"{word}\n")
        
        print(f"Created {output_filename} with {len(words)} entries")


#Function that takes a txt file and removes all duplicates and lower cases all words and saves to same file

def remove_duplicates(input_filename):
    # Read the input file
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Remove duplicates and convert to lowercase
    unique_words = set()
    for line in lines:
        unique_words.add(line.strip().lower())
    
    # Write the unique words back to the file
    with open(input_filename, 'w', encoding='utf-8') as file:
        for word in sorted(unique_words):
            file.write(f"{word}\n")
    
    print(f"Removed duplicates and saved to {input_filename}")


if __name__ == "__main__":
    import sys
    
    # if len(sys.argv) != 2:
    #     print("Usage: python script.py input_file.txt")
    #     sys.exit(1)
    
    # input_file = sys.argv[1]
    # process_file(input_file)
    # print("Processing complete!")

    remove_duplicates("lists/brand.txt")
    remove_duplicates("lists/drug.txt")
    remove_duplicates("lists/drug_n.txt")
    remove_duplicates("lists/group.txt")
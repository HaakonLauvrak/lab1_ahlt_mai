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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python script.py input_file.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_file(input_file)
    print("Processing complete!")
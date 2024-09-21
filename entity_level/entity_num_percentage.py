import os
import json
import re
import logging

# Set up logging
logging.basicConfig(filename='shenyuge/lingyue-data-process/entity_level/logs/entity_number_percentage.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Directory containing the JSON files
json_directory = '/home/shenyuge/lingyue-data-process/entity_level'

# Function to check if a string contains numbers (excluding stock numbers)
def has_number(entity):
    # Regular expression for matching numbers (float or percentage)
    number_pattern = r'(\d+\.\d+|\d+%)'
    stock_number_pattern = r'^\d+$'  # Matches stock numbers (only digits)

    if re.search(number_pattern, entity):
        if not re.match(stock_number_pattern, entity):
            return True
    return False

# Recursive function to count entities with numbers
def count_entities_with_numbers(entities):
    total_count = 0
    number_count = 0

    for entity in entities:   #TODO 递归 entity
        total_count += 1
        if has_number(entity['entity']):
            number_count += 1
        
        # Check subentities
        if 'subentity' in entity and entity['subentity']:
            sub_total, sub_number = count_entities_with_numbers(entity['subentity'])
            total_count += sub_total
            number_count += sub_number

    return total_count, number_count

# Process all JSON files in the specified directory
for filename in os.listdir(json_directory):
    if filename.endswith('.json'):
        file_path = os.path.join(json_directory, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Initialize counters for this file
            total_entities = 0
            entities_with_numbers = 0

            # Process each paragraph in the JSON data
            for item in data:
                if 'entities' in item:
                    total, numbers = count_entities_with_numbers(item['entities'])
                    total_entities += total
                    entities_with_numbers += numbers

            # Calculate the percentage
            if total_entities > 0:
                percentage = (entities_with_numbers / total_entities) * 100
            else:
                percentage = 0

            # Log the results for this file
            logging.info(f"File: {filename}")
            logging.info(f"Total entities: {total_entities}")
            logging.info(f"Entities with numbers (excluding stock numbers): {entities_with_numbers}")
            logging.info(f"Percentage of entities with numbers: {percentage:.2f}%")
            logging.info("")

        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}")

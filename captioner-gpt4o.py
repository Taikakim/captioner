import os
import re
from PIL import Image

# Define the directory where the png and txt files are located
input_directory = './input_images'  # Replace with your input directory
output_directory = './output'  # Output directory for .caption files

# Function to clean up the prompt text by removing unwanted characters
def clean_prompt(prompt):
    return prompt.replace("'", "").replace("[", "").replace("]", "")

# Function to extract text prompts and create .caption files
def create_caption_files(input_directory, output_directory):
    unprocessed_files = []  # List to hold files that do not match the naming scheme

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    for file in os.listdir(input_directory):
        if file.endswith('.png'):
            base_name = file.rsplit('.', 1)[0]

            # Debugging: Print the current file being processed
            print(f'Processing file: {file}')

            # Check for "randomized_prompt" and "prompt" in PNG file metadata
            caption_content = None  # Initialize with None to check later if metadata exists
            try:
                with Image.open(os.path.join(input_directory, file)) as img:
                    randomized_prompt = img.info.get('randomized_prompt')
                    if randomized_prompt:
                        # Clean the "randomized_prompt" and use it as the caption content
                        caption_content = clean_prompt(randomized_prompt)
                    else:
                        prompt = img.info.get('prompt')
                        if prompt:
                            # Clean the "prompt" and use it as the caption content
                            caption_content = clean_prompt(prompt)
            except Exception as e:
                print(f'Error reading metadata from {file}: {e}')
                unprocessed_files.append(file)
                continue

            if not caption_content:
                # Attempt using batch pattern
                match = re.match(r'(.*\(\d+\))(_\d+)?\.png', file)
                if match:
                    batch_name = match.group(1)
                    settings_filename = f'{batch_name}_settings.txt'
                    settings_filepath = os.path.join(input_directory, settings_filename)

                    # Debugging: Print the batch name and settings file path
                    print(f'Batch name: {batch_name}')
                    print(f'Settings file path: {settings_filepath}')

                    # Verify the settings file exists
                    if os.path.exists(settings_filepath):
                        with open(settings_filepath, 'r') as settings_file:
                            settings_data = settings_file.read()

                            # Extract the text_prompts section from the settings data
                            match = re.search(r'"text_prompts":\s*\{\s*"0":\s*\[(.*?)\]\s*\}', settings_data, re.DOTALL)
                            if match:
                                # Get the individual prompts, remove quotes, weights, and whitespace
                                prompts = [re.sub(r':\s*-?\d+(\.\d+)?', '', prompt.strip('" \n')) for prompt in match.group(1).split(',')]
                                # Clean the prompts and join them
                                caption_content = ': '.join(clean_prompt(prompt) for prompt in prompts)
                            else:
                                print(f'No text prompts found in settings file: {settings_filename}')
                                unprocessed_files.append(file)
                    else:
                        print(f'Settings file not found for image: {file}')
                        unprocessed_files.append(file)

                else:
                    # Fallback: Attempt to directly use settings file for simple names
                    settings_filename = f"{base_name}_settings.txt"
                    settings_filepath = os.path.join(input_directory, settings_filename)
                    if os.path.exists(settings_filepath):
                        with open(settings_filepath, 'r') as settings_file:
                            settings_data = settings_file.read()
                            # Extract the text_prompts section from the settings data
                            match = re.search(r'"text_prompts":\s*\{\s*"0":\s*\[(.*?)\]\s*\}', settings_data, re.DOTALL)
                            if match:
                                prompts = [re.sub(r':\s*-?\d+(\.\d+)?', '', prompt.strip('" \n')) for prompt in match.group(1).split(',')]
                                caption_content = ': '.join(clean_prompt(prompt) for prompt in prompts)
                            else:
                                print(f'No text prompts found in settings file: {settings_filename}')
                                unprocessed_files.append(file)
                    else:
                        # Manual intervention for unmatched pattern
                        unprocessed_files.append(file)
                        print(f'Regex did not match for file: {file}. Manual processing needed.')

            if caption_content:
                # Create the .caption file in the output directory
                caption_filename = f'{base_name}.caption'
                caption_filepath = os.path.join(output_directory, caption_filename)
                with open(caption_filepath, 'w', encoding='utf-8') as caption_file:
                    caption_file.write(caption_content)
                print(f'Caption file created: {caption_filename}')

    # After processing all files, print the unprocessed files
    if unprocessed_files:
        print("\nThe following files did not match the naming scheme or had other issues and need manual processing:")
        for filename in unprocessed_files:
            print(filename)

# Call the function with fallback mechanism
create_caption_files(input_directory, output_directory)

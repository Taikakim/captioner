import os
import re
import json

# Define the directory where the png and txt files are located
directory = './'  # Replace with your directory

# Function to extract text prompts and create .caption files
def create_caption_files(directory):
    for file in os.listdir(directory):
        if file.endswith('.png'):
            base_name = file.rsplit('.', 1)[0]
            # Extract the batch identifier from the image filename
            match = re.match(r'(.*\(\d+\))_\d+\.png', file)
            if match:
                batch_name = match.group(1)
                settings_filename = f'{batch_name}_settings.txt'
                settings_filepath = os.path.join(directory, settings_filename)

                # Verify the settings file exists
                if os.path.exists(settings_filepath):
                    with open(settings_filepath, 'r') as settings_file:
                        settings_data = settings_file.read()

                        # Extract the text_prompts section from the settings data
                        match = re.search(r'"text_prompts":\s*\{\s*"0":\s*\[(.*?)\]\s*\}', settings_data, re.DOTALL)
                        if match:
                            # Get the individual prompts, remove quotes, weights and whitespace
                            prompts = [re.sub(r':\s*-?\d+(\.\d+)?', '', prompt.strip('" \n')) for prompt in match.group(1).split(',')]
                            caption_content = ', '.join(prompts)

                            # Create the .caption file
                            caption_filename = f'{base_name}.caption'
                            caption_filepath = os.path.join(directory, caption_filename)
                            with open(caption_filepath, 'w', encoding='ascii') as caption_file:
                                caption_file.write(caption_content)
                            print(f'Caption file created: {caption_filename}')
                else:
                    print(f'Settings file not found for image: {file}')
            else:
                print(f'Could not extract batch identifier from file: {file}')

# Call the function
create_caption_files(directory)

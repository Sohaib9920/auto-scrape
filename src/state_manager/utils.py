from bs4 import BeautifulSoup
import os
import base64


def save_formatted_html(html_content, output_file_name):
    soup = BeautifulSoup(html_content, "html.parser")
    formatted_html = soup.prettify()

    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(formatted_html)


def save_markdown(markdown_content, output_file_name):

    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(markdown_content)


def save_conversation(input_messages, model_output, output_file_name):
    with open(output_file_name, 'w', encoding='utf-8') as f:
        for message in input_messages:
            role = message["role"]
            content = message["content"]
            f.write(f'{role}:\n')
            if isinstance(content, list):
                for msg in content:
                    msg_type = msg["type"] 
                    if msg_type == "image_url":
                        f.write(f'\t{msg_type}:\n{{Image URL}}\n')
                    else:
                        f.write(f'\t{msg_type}:\n{msg[msg_type]}\n')
                f.write("\n")   
            else:
                f.write(f'{content}\n\n')  
        f.write(f'Model output:\n{model_output}')


def encode_image(image_path):
	"""Encode image to base64 string"""
	with open(image_path, 'rb') as image_file:
		return base64.b64encode(image_file.read()).decode('utf-8')

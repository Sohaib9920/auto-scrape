from bs4 import BeautifulSoup
import os


def save_formatted_html(html_content, output_file_name):
	soup = BeautifulSoup(html_content, 'html.parser')
	formatted_html = soup.prettify()

	if not os.path.exists('temp'):
		os.makedirs('temp')

	with open('temp/' + output_file_name, 'w', encoding='utf-8') as f:
		f.write(formatted_html)


def save_markdown(markdown_content, output_file_name):
	if not os.path.exists('temp'):
		os.makedirs('temp')

	with open('temp/' + output_file_name, 'w', encoding='utf-8') as f:
		f.write(markdown_content)
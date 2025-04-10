from bs4 import BeautifulSoup
import os


def save_formatted_html(html_content, output_file_name):
    soup = BeautifulSoup(html_content, "html.parser")
    formatted_html = soup.prettify()

    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(formatted_html)


def save_markdown(markdown_content, output_file_name):

    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(markdown_content)


def save_conversation(input_messages, response, filename):

    text = "\n\n".join(
        [f"{msg['role']}:\n{msg['content']}" for msg in input_messages]
        + [f"Model output:\n{response}"]
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

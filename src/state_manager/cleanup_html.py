from bs4 import BeautifulSoup, Comment, Tag
import re

def cleanup_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    initial_size = len(str(soup))

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove unwanted tags completely
    unwanted_tags = ["style", "script", "font", "link", "meta"]
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove nested wrapper tags
    def is_wrapper_tag(tag):
        children = tag.contents 
        return (
            len(children) == 1 
            and isinstance(children[0], Tag)
            and not tag.get("id")
            and not tag.get("class")
        )
    for tag in soup.find_all(["div", "span"]):
        if is_wrapper_tag(tag):
            tag.replace_with(tag.contents[0])  

    # Add counter for class enumeration
    class_counter = 0

    # Remove all attributes except allowed ones
    allowed_attrs = [
        "id",
        "name",
        "href",
        "alt"
    ]

    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)

        for attr in attrs:
            if attr == "class":
                tag["c"] = str(class_counter)
                class_counter += 1
                del tag[attr]
                
            elif attr not in allowed_attrs:
                del tag[attr]   
    
    cleaned_html = str(soup)

    # Remove multiple spaces and newlines
    cleaned_html = " ".join(cleaned_html.split())

    # Remove empty tags
    empty_tags_pattern = r"<[^/>][^>]*>\s*</[^>]+>"
    cleaned_html = re.sub(empty_tags_pattern, "", cleaned_html)

    final_size = len(cleaned_html)
    print(f"Size reduced by {100 - (final_size * 100//initial_size)}%")

    return cleaned_html
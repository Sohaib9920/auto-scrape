from bs4 import BeautifulSoup, Tag, NavigableString
from selenium import webdriver
from pydantic import BaseModel


class Element(BaseModel):
    index: int
    content: str
    addition: bool = False
    n_parents: int = 0

    def get_text(self) -> str:
        return (
            ("(+)" if self.addition else "   ")  + 
            f"{self.index:>4}:" + 
            "\t"*self.n_parents + 
            self.content
        )


class ProcessedDomContent(BaseModel):
    interactable_elements: list[Element]
    selector_map: dict[int, str]


class DomService:
    """
    Process the html to only give interactable/leaf nodes and their selector mapping.
    Use `only_top` argument to only consider stuff seen at front.
    """

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_current_state(self, only_top: bool = True) -> ProcessedDomContent:
        html_content = self.driver.page_source
        return self._process_content(html_content, only_top)

    def _process_content(
        self, html_content: str, only_top: bool = True
    ) -> ProcessedDomContent:
        soup = BeautifulSoup(html_content, "html.parser")

        # Traversing
        # similar to descendants except stop traversing the nodes which are not accepted
        candidate_elements: list[Tag | NavigableString] = []
        dom_queue = list(soup.body.children)[::-1] # .contents may give unexpected behaviour when modifying
        while dom_queue:
            elem = dom_queue.pop()

            if isinstance(elem, Tag):
                if not self._is_element_accepted(elem):
                    elem.decompose()
                    continue

                for child in reversed(list(elem.children)):
                    dom_queue.append(child)

                if self._is_interactive_element(elem) or self._is_leaf_element(elem):
                    if self._is_active(elem):
                        candidate_elements.append(elem)

            elif isinstance(elem, NavigableString) and elem.get_text(strip=True):
                candidate_elements.append(elem)

        # filtering and creating selector mapping
        interactable_elements = []
        selector_map = {}

        for index, elem in enumerate(candidate_elements):

            if isinstance(elem, NavigableString) and elem.parent in candidate_elements:
                continue  # happers for texts inside leaf nodes

            xpath = self._generate_xpath(elem)

            if isinstance(elem, NavigableString):
                if not self._is_visible_text(elem, xpath, top=only_top):
                    continue
                text_content = elem.strip()
                if text_content:
                    interactable_elements.append(Element(index=index, content=text_content))

            else:
                if not self._is_visible_element(xpath, top=only_top):
                    continue
                tag_name = elem.name
                text_content = elem.get_text(strip=True, separator=" | ")
                attributes = self._get_essential_attributes(elem)
                elm_content = f'<{tag_name}{" " + attributes if attributes else ""}>{text_content}</{tag_name}>'
                interactable_elements.append(Element(index=index, content=elm_content))

            selector_map[index] = xpath

        return ProcessedDomContent(
            interactable_elements=interactable_elements, selector_map=selector_map
        )

    def _is_element_accepted(self, element: Tag) -> bool:
        leaf_element_deny_list = {"svg", "iframe", "script", "style", "link"}
        return element.name not in leaf_element_deny_list

    def _is_interactive_element(self, element: Tag) -> bool:
        interactive_elements = {
            "a",
            "button",
            "details",
            "embed",
            "input",
            "label",
            "menu",
            "menuitem",
            "object",
            "select",
            "textarea",
            "summary",
        }
        interactive_roles = {
            "button",
            "menu",
            "menuitem",
            "link",
            "checkbox",
            "radio",
            "slider",
            "tab",
            "tabpanel",
            "textbox",
            "combobox",
            "grid",
            "listbox",
            "option",
            "progressbar",
            "scrollbar",
            "searchbox",
            "switch",
            "tree",
            "treeitem",
            "spinbutton",
            "tooltip",
        }

        return (
            element.name in interactive_elements
            or element.get("role") in interactive_roles
            or element.get("aria-role") in interactive_roles
        )

    def _is_leaf_element(self, element: Tag) -> bool:
        if not element.get_text(strip=True):
            return False

        # Check for simple text-only elements
        children = list(element.children)
        if len(children) == 1 and isinstance(children[0], str):
            return True

        return False

    def _is_active(self, element: Tag) -> bool:
        return not (
            element.get("disabled") is not None
            or element.get("hidden") is not None
            or element.get("aria-disabled") == "true"
        )

    def _generate_xpath(self, element: Tag | NavigableString) -> str:
        if isinstance(element, NavigableString):
            if element.parent:
                return self._generate_xpath(element.parent)
            return ""

        xpath_segments = []
        current = element

        while True:
            if current.name == "[document]":
                break

            position = len(current.find_previous_siblings(current.name)) + 1
            segment = f"{current.name}[{position}]"
            xpath_segments.append(segment)
            current = current.parent

        xpath = "//" + "/".join(xpath_segments[::-1])

        return xpath

    def _get_essential_attributes(self, element: Tag) -> str:
        essential_keys = [
 			'id',
 			# 'class',
 			'href',
 			'src',
 			'aria-label',
 			'aria-name',
 			'aria-role',
 			'aria-description',
 			'aria-expanded',
 			'aria-haspopup',
 			'readonly',
 			'disabled',
 			'checked',
 			'selected',
 			'role',
 			'type',  # Important for inputs, buttons
 			'name',  # Important for form elements
 			'value',  # Current value of form elements
 			'placeholder',  # Helpful for understanding input purpose
 			'title',  # Additional descriptive text
 			'alt',  # Alternative text for images
 			'for',  # Important for label associations
 			'autocomplete',  # Form field behavior
 		]
        essential_prefixes = ('aria-', 'data-',)

        attrs = []
        for attr, value in element.attrs.items():
            if attr in essential_keys or attr.startswith(essential_prefixes):
                attrs.append(f'{attr}="{value}"')

        return " ".join(attrs)

    def _is_visible_text(self, element: NavigableString, xpath: str, top: bool) -> bool:
        # top creates bounding box around the text node and checks if it is at the front of screen
        parent = element.parent
        index = list(parent.children).index(element)

        js_code = """
            function checkVisibleText(xpath, index, top) {
                const parent = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (!parent) {
                    return false;
                }

                const visible = parent.checkVisibility({
                    checkOpacity: true,
                    checkVisibilityCSS: true
                });

                if (!visible) {
                    return false;
                }

                if (top) {
                    const range = document.createRange();
                    const textNode = parent.childNodes[index];
                    range.selectNodeContents(textNode);
                    const rect = range.getBoundingClientRect();

                    
                    if (rect.width === 0 || rect.height === 0 || 
                        rect.top < 0 || rect.top > window.innerHeight) {
                        return false;
                    }

                    const middleX = rect.left + rect.width / 2;
                    const middleY = rect.top + rect.height / 2;
                    const topElement = document.elementFromPoint(middleX, middleY);

                    if (!topElement || (!parent.contains(topElement) && !topElement.contains(parent))) {
                        return false;
                    }
                }

                return true;
            }
            return checkVisibleText(arguments[0], arguments[1], arguments[2]);
        """
        try:
            visble = self.driver.execute_script(js_code, xpath, index, top)
            return bool(visble)
        except Exception as e:
            print(
                f"Error occured in top text check of {xpath}: {parent}: {index}: {element}: {e}"
            )
            return False

    def _is_visible_element(self, xpath: str, top: bool) -> bool:
        # top checks if element is at the front of screen and can be clicked i.e not blocked by some popup
        js_code = """
            function checkVisibleElement(xpath, top) {
                const elem = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (!elem) {
                    return false;
                }
                
                const visible = elem.checkVisibility({
                    checkOpacity: true,
                    checkVisibilityCSS: true
                });
                
                if (!visible) {
                    return false;
                }

                if (top) {
                    const rect = elem.getBoundingClientRect();
                    const points = [
                        {x: rect.left + rect.width * 0.25, y: rect.top + rect.height * 0.25},
                        {x: rect.left + rect.width * 0.75, y: rect.top + rect.height * 0.25}, 
                        {x: rect.left + rect.width * 0.25, y: rect.top + rect.height * 0.75},
                        {x: rect.left + rect.width * 0.75, y: rect.top + rect.height * 0.75},
                        {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2}
                    ];
                    
                    return points.some(point => {
                        const topEl = document.elementFromPoint(point.x, point.y);
                        return elem.contains(topEl);
                    });
                }

                return true;
            }
            return checkVisibleElement(arguments[0], arguments[1]);
        """
        try:
            visible = self.driver.execute_script(js_code, xpath, top)
            return bool(visible)
        except Exception as e:
            print(f"Error occured in visibility check of {xpath}: {e}")
            return False

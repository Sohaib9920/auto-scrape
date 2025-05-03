from bs4 import BeautifulSoup, Tag, NavigableString
from selenium import webdriver
from pydantic import BaseModel
from typing import Any


class DomContentItem(BaseModel):
    index: int
    text: str
    clickable: bool
    n_parents: int
    addition: bool = False


class ProcessedDomContent(BaseModel):
	items: list[DomContentItem]
	selector_map: dict[int, str]

	def dom_items_to_string(self) -> str:
		formatted_text = ""
		for item in self.items:
			indent = "\t"*item.n_parents
			formatted_text += f"{'(+) ' if item.addition else ' '*4}{item.index if item.clickable else '_':>3}:{indent}{item.text}\n"
		return formatted_text
    

class DomService:
    """
    Process the html to only give dom elements and their selector mapping.
    """

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_current_state(self) -> ProcessedDomContent:
        html_content = self.driver.page_source
        return self._process_content(html_content)

    def _process_content(self, html_content: str) -> ProcessedDomContent:
        soup = BeautifulSoup(html_content, "lxml")

        candidate_elements: list[Tag | NavigableString] = []
        dom_queue = list(soup.body.children)[::-1] if soup.body else []

        # do not decompose otherwise wrong element index when using `_generate_xpath` and `checkTextFront`
        while dom_queue:
            element = dom_queue.pop()

            if not self._quick_element_filter(element):
                continue 

            # Handle both Tag elements and text nodes
            if isinstance(element, Tag):
                if not self._is_element_accepted(element):
                    continue

                for child in reversed(list(element.children)):
                    dom_queue.append(child)

                if self._is_interactive_element(element):
                    candidate_elements.append(element)
            
            elif isinstance(element, NavigableString) and element.strip():
                candidate_elements.append(element)
        
        candidates = [
            {
                "xpath": self._generate_xpath(c),
                "is_text": not isinstance(c, Tag),
                "node_index": list(c.parent.children).index(c),
            }
            for c in candidate_elements
        ]

        mask = self.check_visibility_js(candidates)

        accepted = [
            {
                "xpath": c["xpath"],
                "is_text": c["is_text"],
                "node_index": c["node_index"],
                "element": e,
                
            }
            for e, c, included in 
            zip(candidate_elements, candidates, mask) if included
        ]

        xpaths = set(a["xpath"] for a in accepted)
        output_items = []
        selector_map = {}

        for index, a in enumerate(accepted):
            is_text = a["is_text"]
            elem = a["element"]
            xpath = a["xpath"]
            n_parents = sum(elem_xpath in xpath for elem_xpath in xpaths if elem_xpath != xpath)
            
            if is_text:
                text = self._cap_text_length(elem.strip())
                output_items.append(
                    DomContentItem(index=index, text=text, clickable=False, n_parents=n_parents)
                )
            else:
                tag_name = elem.name
                text = self._cap_text_length(elem.get_text(strip=True, separator=" | "))
                attributes = self._get_essential_attributes(elem)
                elm_content = f'<{tag_name}{" " + attributes if attributes else ""}>{text}</{tag_name}>'
                output_items.append(
                    DomContentItem(index=index, text=elm_content, clickable=True, n_parents=n_parents)
                )
            
            selector_map[index] = xpath  
        
        content = ProcessedDomContent(items=output_items, selector_map=selector_map)

        return content

    def _quick_element_filter(self, element: Tag|NavigableString) -> bool:
        """
        Quick pre-filter to eliminate elements before expensive checks.
        Returns True if element passes initial filtering.
        """
        if isinstance(element, NavigableString):
            return bool(element.strip())
        
        # Quick attribute checks that would make element invisible/non-interactive
        style = element.get('style', '')
        if any(
            [
                element.get('aria-hidden') == 'true',
                element.get('hidden') is not None,
                element.get('disabled') is not None,
                'display: none' in style or 'visibility: hidden' in style,
                any(cls in element.get('class', []) for cls in ['hidden', 'invisible']),
                element.get('type') == 'hidden',
            ]
        ):
            return False
        
        return True

    def _is_element_accepted(self, element: Tag) -> bool:
        """Check if element is accepted based on tag name and special cases."""
        leaf_element_deny_list = {'svg', 'iframe', 'script', 'style', 'link', 'meta'}
        return element.name not in leaf_element_deny_list

    def _is_interactive_element(self, element: Tag) -> bool:
        """Check if element is interactive based on tag name and attributes."""
        interactive_elements = {
            'a', 'button', 'details', 'embed', 'input', 'label', 'menu', 'menuitem',
            'object', 'select', 'textarea', 'summary', 'dialog'
        }
        interactive_roles = {
            'button', 'menu', 'menuitem', 'link', 'checkbox', 'radio', 'slider', 'tab',
            'tabpanel', 'textbox', 'combobox', 'grid', 'listbox', 'option', 'progressbar',
            'scrollbar', 'searchbox', 'switch', 'tree', 'treeitem', 'spinbutton', 'tooltip',
            'dialog', 'alertdialog', 'menuitemcheckbox', 'menuitemradio', 'list', 'listitem'
        }

        return (
            element.name in interactive_elements
            or element.get('role') in interactive_roles
            or element.get('tabindex') == '0'
        )

    def _generate_xpath(self, element: Tag) -> str:
        # pages like wiki have multiple elements associated with single id
        if isinstance(element, NavigableString):
            return self._generate_xpath(element.parent) if element.parent else ''
        
        parts = []
        current = element

        while current.name != '[document]':
            selector = current.name
            position = len(current.find_previous_siblings(current.name)) + 1
            selector += f'[{position}]'
            current = current.parent
            parts.append(selector)

        return  '//' + '/'.join(reversed(parts)) if parts else ''
    
    def check_visibility_js(self, candidates: list[dict[str, Any]]) -> list[bool]:
        js_code = """
        function checkTop(elem) {
            const rect = elem.getBoundingClientRect();

            const points = [
                {x: rect.left + rect.width * 0.2, y: rect.top + rect.height * 0.2},
                {x: rect.left + rect.width * 0.8, y: rect.top + rect.height * 0.2}, 
                {x: rect.left + rect.width * 0.2, y: rect.top + rect.height * 0.8},
                {x: rect.left + rect.width * 0.8, y: rect.top + rect.height * 0.8},
                {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2}
            ];
            
            return points.some(point => {
                const topEl = document.elementFromPoint(point.x, point.y);
                return elem.contains(topEl);
            });
        }

        function checkTextFront(textNode) {
            const range = document.createRange();
            range.selectNodeContents(textNode);
            const rect = range.getBoundingClientRect();
            
            return (
                rect.width !== 0 && 
                rect.height !== 0 &&
                rect.top > 0 &&
                rect.bottom < window.innerHeight
            );
        }

        function checkVisibility(candidates) {
            const results = [];
            const elementCache = new Map();
            const accepted_elem_xpaths = new Set();

            for (const candidate of candidates) {
                const xpath = candidate.xpath;
                let elem;

                if (candidate.is_text) {
                    let skip = false;
                    for (const accepted_xpath of accepted_elem_xpaths) {
                        if (xpath.startsWith(accepted_xpath)) {
                            skip = true;
                            break;              
                        }
                    }
                    if (skip) {
                        results.push(false);
                        continue;
                    }
                }

                if (accepted_elem_xpaths.has(xpath)) {
                    results.push(false);
                    continue;
                }

                if (elementCache.has(xpath)) {
                    elem = elementCache.get(xpath);
                    
                } else {
                    elem = document.evaluate(
                        xpath,
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;

                    elementCache.set(xpath, elem);
                }

                if (!elem) {
                    results.push(false);
                    continue;
                }

                const isVisible = elem.checkVisibility({
                    checkOpacity: true,
                    checkVisibilityCSS: true
                })

                if (!isVisible) {
                    results.push(false);
                    continue;
                }

                if (candidate.is_text) {
                    const textNode = elem.childNodes[candidate.node_index];
                    const isFrontText = checkTextFront(textNode);

                    if (!isFrontText) {
                        results.push(false);
                        continue;
                    }
                } else {
                    const isTop = checkTop(elem);

                    if (!isTop) {
                        results.push(false);
                        continue;
                    }
                }

                results.push(true)

                if (!candidate.is_text) {
                    accepted_elem_xpaths.add(xpath)     
                }
                
                // console.log(elem)
            }
            return results;
        }

        const candidates = arguments[0]
        return checkVisibility(candidates)
        """
        mask = self.driver.execute_script(js_code, candidates)
        return mask
    
    def _get_essential_attributes(self, element: Tag) -> str:
        essential_attributes = [
            'id',
            # 'class',
            'href',
            'src',
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
            if attr in essential_attributes or attr.startswith(essential_prefixes):
                if isinstance(value, str):
                    value = value[:50]
                elif isinstance(value, (list, tuple)):
                    value = ' '.join(str(v)[:50] for v in value)
                attrs.append(f'{attr}="{value}"')
        
        return ' '.join(attrs)
    
    def _cap_text_length(self, text: str, max_length: int = 150) -> str:
        if len(text) > max_length:
            half_length = max_length // 2
            return text[:half_length] + '...' + text[-half_length:]
        return text

            
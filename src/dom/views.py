from pydantic import BaseModel


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
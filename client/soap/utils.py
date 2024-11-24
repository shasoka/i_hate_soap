from lxml import etree
from lxml.etree import _Element


def element_to_string(et_elem: _Element) -> str | _Element:
    try:
        # Преобразование элемента в строку, сохраняя все неймспейсы
        xml_as_str: str = etree.tostring(
            et_elem,
            encoding="utf-8",
            pretty_print=True,
            xml_declaration=True,
        ).decode("utf-8")
        return "\n".join(
            [line for line in xml_as_str.split("\n") if line.strip()]
        )
    except Exception:
        return et_elem


def extract_tag_from_xml(
    et_elem: _Element,
    target_tag: str,
) -> str:
    try:
        xml_str = element_to_string(et_elem)
        xml_str_without_declaration = "\n".join(xml_str.split("\n")[1:])
        root = etree.fromstring(xml_str_without_declaration)
        # Ищем элемент с нужным тегом
        for element in root.iter():
            if element.tag.endswith(target_tag):
                return element.text
    except Exception as e:
        print(f"Ошибка при извлечении токена: {e}")
    return ""

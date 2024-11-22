import xml.etree.ElementTree as ET  # noqa
from xml.dom.minidom import parseString


# noinspection PyBroadException
def format_xml(xml_string: str) -> str:
    try:
        dom = parseString(xml_string)
        return dom.toprettyxml()
    except Exception:
        return xml_string


def extract_token_from_xml(
    xml_string: str,
    target_tag: str,
) -> str:
    try:
        root = ET.fromstring(xml_string)
        for element in root.iter():
            if element.tag.endswith(target_tag):
                return element.text
    except Exception as e:
        print(f"Ошибка при извлечении токена: {e}")
    return ""

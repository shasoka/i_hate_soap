from io import BytesIO

from fastapi import UploadFile
from lxml import etree
from lxml.etree import _Element
from twisted.python import log


def fastapi_file_type_to_bytesio(file: UploadFile) -> BytesIO:
    contents = file.file.read()
    temp_file = BytesIO()
    temp_file.write(contents)
    temp_file.seek(0)
    return temp_file


def restore_xml_string(xml_str: str) -> str:
    return xml_str[: xml_str.rfind("<")] + "</soap11env:Envelope>"


def element_to_string(et_elem: _Element | str) -> str | _Element:
    if isinstance(et_elem, str):
        try:
            xml_str_without_declaration = "\n".join(et_elem.split("\n")[1:])
            if not xml_str_without_declaration.endswith(">"):
                log.msg("[KOSTYLY] Corrupted envelope")
                xml_str_without_declaration = restore_xml_string(
                    xml_str_without_declaration
                )
            et_elem: _Element = etree.fromstring(xml_str_without_declaration)
        except Exception as e:
            print(e)
            return et_elem
    try:
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

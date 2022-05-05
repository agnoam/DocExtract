from typing import Any, Final

from zipfile import ZipFile
import xml.etree.ElementTree as ET
import lxml.etree as etree
from io import StringIO

def xml_extract_namespaces(xml_content: bytes) -> dict[str, str]:
    """
        This function extracts the namespaces from the xml's parent tag and returns them as dictionary.

        args: 
            - `xml_content: bytes` - the xml content (in bytes)

        returns: dictionary - { 'name-name': 'value' }
    """
    return dict([
        node for _, node in ET.iterparse(
            StringIO(xml_content.decode("utf-8") ), events=['start-ns']
        )
    ])

def get_values_by_xpath(xml_content: bytes, xpath_query: str) -> list[any]:
    """
        This function extracts values from the XML by xpath query.

        args:
            - `xml_content: bytes` - the xml content (in bytes)
            - `xpath_query: str` - string of the xpath query

        returns: List of all values matching the query
    """
    namespaces: dict[str, str] = xml_extract_namespaces(xml_content)
    tree = etree.fromstring(xml_content)
    return tree.xpath(xpath_query, namespaces=namespaces)

def extract_strings_by_style(docx_path: str, styles_names: list[str]) -> list[Any]:
    """
        Extracts strings from docx file, by style names
        args:
            - `docx_path: str` - The path of the docx file
            - `styles_names: list[str]` - List of styles names

        returns: Dictionary of all style names with it's hits   
    """
    # DOCX_PATH: Final[str] = r'C:\Users\joe\Desktop\DocExtract\assets\יש לנו טקסט מוזר.docx'
    STYLES_XML_PATH: Final[str] = 'word/styles.xml'
    DOCUMENT_XML_PATH: Final[str] = 'word/document.xml'

    ARCHIVE: Final[ZipFile] = ZipFile(docx_path, 'r')
    STYLES_CONTENT: Final[bytes] = ARCHIVE.read(STYLES_XML_PATH)
    DOCUMENT_CONTENT: Final[bytes] = ARCHIVE.read(DOCUMENT_XML_PATH)

    # { [type_name: string]: [words] }
    results: dict[str, list[str]] = {}
    for style_name in styles_names:
        style_name: str = ''
        STYLE_XPATH_QUERY: Final[str] = f".//*[contains(@w:val,'{style_name}')]/../w:link/@w:val"
        style_ids: list[str] = get_values_by_xpath(STYLES_CONTENT, STYLE_XPATH_QUERY)

        for style_id in style_ids:
            DOCUMENT_XPATH_QUERY: Final[str] = f".//*[@w:val='{style_id}']/../../w:t/text()"
            elements: list[str] = get_values_by_xpath(DOCUMENT_CONTENT, DOCUMENT_XPATH_QUERY)
            
            if elements:
                print(f'found values: {elements} of type style {style_id}')
                results[style_name] = elements

    return results
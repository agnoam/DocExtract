from typing import Final

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

        returns: list of all values matching the query
    """
    
    namespaces: dict[str, str] = xml_extract_namespaces(xml_content)
    tree = etree.fromstring(xml_content)
    return tree.xpath(xpath_query, namespaces=namespaces)

DOCX_PATH: Final[str] = r'C:\Users\joe\Desktop\DocExtract\assets\יש לנו טקסט מוזר.docx'
ARCHIVE: Final[ZipFile] = ZipFile(DOCX_PATH, 'r')
STYLES_CONTENT: Final[bytes] = ARCHIVE.read('word/styles.xml')
DOCUMENT_CONTENT: Final[bytes] = ARCHIVE.read('word/document.xml')

style_name: str = ''
STYLE_XPATH_QUERY: Final[str] = f".//*[contains(@w:val,'{style_name}')]/../w:link/@w:val"
style_ids: list[str] = get_values_by_xpath(STYLES_CONTENT, STYLE_XPATH_QUERY)

for style_id in style_ids:
    DOCUMENT_XPATH_QUERY: Final[str] = f".//*[@w:val='{style_id}']/../../w:t/text()"
    elements: list[str] = get_values_by_xpath(DOCUMENT_CONTENT, DOCUMENT_XPATH_QUERY)
    
    print(f'found values: {elements} of type style {style_id}')
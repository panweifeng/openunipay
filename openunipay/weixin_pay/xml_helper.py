from xml.dom.minidom import getDOMImplementation
from xml.etree import ElementTree

_xmldom_impl = getDOMImplementation()

def dict_to_xml(valueDict):
    doc = _xmldom_impl.createDocument(None, 'xml', None)
    topElement = doc.documentElement
    for (key, value) in valueDict.items():
        element = doc.createElement(key)
        element.appendChild(doc.createTextNode(str(value)))
        topElement.appendChild(element)
    return topElement.toxml()

def xml_to_dict(xmlContent):
    result = {}
    root = ElementTree.fromstring(xmlContent)
    for child in root:
        result[child.tag] = child.text
    return result
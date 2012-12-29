from xml.etree import ElementTree

# Module Code:


class DictionaryXml(dict):
    """
    Adds object like functionality to the standard dictionary.
    """

    def __init__(self, start_dic = None):
        """Starting"""
        if start_dic is None:
            start_dic = {}
        dict.__init__(self, start_dic)

    def __getattr__(self, item):
        """Get Attributes"""
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        """Set Attributes"""
        self.__setitem__(item, value)

    def __str__(self):
        """Get or Set"""
        if '_text' in self:
            return self.__getitem__('_text')
        else:
            return ''

    @staticmethod
    def wrap_dict(elem):
        """
        Static method to wrap_dict a dictionary recursively as an DictionaryXml
        """
        if isinstance(elem, dict):
            return DictionaryXml(
                (k, DictionaryXml.wrap_dict(v)) for (k, v) in elem.iteritems())
        elif isinstance(elem, list):
            return [DictionaryXml.wrap_dict(v) for v in elem]
        else:
            return elem

    @staticmethod
    def _unwrap_dict(elem):
        """
        Defined function to help unwrap_dict
        """
        if isinstance(elem, dict):
            return dict(
                (k, DictionaryXml._unwrap_dict(v))
                for (k, v) in elem.iteritems())
        elif isinstance(elem, list):
            return [DictionaryXml._unwrap_dict(v) for v in elem]
        else:
            return elem

    def unwrap_dict(self):
        """
        Recursively converts an DictionaryXml to a standard dictionary
        and returns the result.
        """
        return DictionaryXml._unwrap_dict(self)


def _dicttoxml(parent, elemdict):
    """
    Defined function to help dicttoxml
    """
    assert not isinstance(elemdict, list)

    if isinstance(elemdict, dict):
        for (tag, child) in elemdict.iteritems():
            if str(tag) == '_text':
                parent.text = str(child)
            elif isinstance(child, list):
                # iterate through the array and convert
                for listchild in child:
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _dicttoxml(elem, listchild)
            else:
                elem = ElementTree.Element(tag)
                parent.append(elem)
                _dicttoxml(elem, child)
    else:
        parent.text = str(elemdict)


def dicttoxml(xmldict):
    """
    Converts a dictionary to an XML ElementTree Element
    """

    roottag = xmldict.keys()[0]
    root = ElementTree.Element(roottag)
    _dicttoxml(root, xmldict[roottag])
    return root


def _xmltodict(node, classdict):
    """
    Defined function to help xmltodict
    """
    node_dict = classdict()
    if len(node.items()) > 0:
        # if we have attributes, set them
        node_dict.update(dict(node.items()))

    for child in node:
        # recursively add the element's children
        new_item = _xmltodict(child, classdict)
        if child.tag in node_dict:
            # found duplicate tag, force a list
            if isinstance(node_dict[child.tag], list):
                # append to existing list
                node_dict[child.tag].append(new_item)
            else:
                # convert to list
                node_dict[child.tag] = [node_dict[child.tag], new_item]
        else:
            # only one, directly set the dictionary
            node_dict[child.tag] = new_item

    if node.text is None:
        text = ''
    else:
        text = node.text

    if len(node_dict) > 0:
        # if we have a dictionary add the text as a dictionary
        # value (if there is any)
        if len(text) > 0:
            node_dict['_text'] = text
    else:
        # if we don't have child nodes or attributes, just set the text
        node_dict = text
    return node_dict


def xml_to_dict(root, class_dict=DictionaryXml):
    """
    Converts an XML file or ElementTree Element to a dictionary
    """
    # If a string is passed in, try to open it as a file
    if isinstance(root, basestring):
        root = ElementTree.parse(root).getroot()
    elif not isinstance(root, ElementTree.Element):
        raise Exception('Expected ElementTree.Element or file path string')
    return class_dict({root.tag: _xmltodict(root, class_dict)})

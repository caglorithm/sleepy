
class Parameter:

    def __init__(self, title, fieldType, default):

        self.descriptor = {
            "title" : title,
            "fieldType" : fieldType,
            "default" : default
        }

class ParameterBase:

    def getBuildTree(control):
        """Creates a build tree from the list of paramters declared in a control.
        """

        buildTree = {
            "title" : "Parameters",
            "fields" : {}
        }

        try:
            attributes = vars(control)
        except TypeError:
            return buildTree

        for attribute in attributes:

            ParameterBase.attachAttribute(buildTree, control, attribute)

        return buildTree

    def attachAttribute(buildTree, control, attribute):

        attributeObject = getattr(control, attribute)

        if isinstance(attributeObject, Parameter):

            buildTree["fields"][attribute] = attributeObject.descriptor

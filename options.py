import os
import json
import functools
from java.awt.event import ActionListener
from java.awt.event import ActionEvent;
from ij import IJ
from ij import WindowManager
from ij.gui import GenericDialog
from ij.gui import NonBlockingGenericDialog
from ij.plugin.filter import PlugInFilterRunner


PATH_FIELD_COLUMNS = 30

def rgetattr(obj, attr, *args):
    '''recursive version of getattr, written by https://stackoverflow.com/users/190597/unutbu (Thanks!)
    '''
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))
    
    
def rsetattr(obj, attr, val):
    '''recursive version of setattr, written by https://stackoverflow.com/users/190597/unutbu (Thanks!)
    '''
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)
   

class Options(ActionListener):


    def __init__(self, title):
        super(Options, self).__init__()
        self.title = title
        self.elements = {}
        self.helpUrl = ''
        
        self.dialog = None
        self.path = None
        self.autosave = True
        self.wasCanceled = False
        self.previewPlugin = None
        self.command = ""
        self.nonBlocking = False
        
    
    def getTitle(self):
        return self.title


    def setHelpUrl(self, url):
        self.helpUrl = url


    def getHelpUrl(self):
        return self.helpUrl


    def add(self, option):
        self.elements[option.getKey()] = option
        option.setOrder(self.size())


    def size(self):
        return len(self.elements.keys())


    def asDict(self):
        optionsDict = {}
        for key, option in self.elements.items():
            optionsDict[key] = option.asDict()
        meAsDict = {'title': self.title, 'elements': optionsDict, 'helpUrl': self.helpUrl, 'nonBlocking': self.nonBlocking}
        return meAsDict
    
    
    def asJSON(self):
        data = json.dumps(self.asDict(), indent=4)
        return data
    
    
    def save(self):
        self.saveAs(self.path)
       
       
    def saveAs(self, path):
        with open(path, 'w') as outfile:
            outfile.write(self.asJSON())
       
    
    def addPreviewPlugin(self, aPlugin, command):
        self.previewPlugin = aPlugin
        self.command = command
    
    
    def showDialog(self):
        self.createDialog()
        self.dialog.showDialog()
        if self.dialog.wasCanceled() or self.wasCanceled:
            return None
        for option in self.sortedList():
            option.setValueFromDialog(self.dialog)
        self.autosave = self.dialog.getNextBoolean()
        sourcePath = self.dialog.getNextString()
        destinationPath = self.dialog.getNextString()
        if sourcePath and sourcePath != self.path and os.path.exists(sourcePath) and sourcePath.endswith(".json"):
            options = Options.fromFile(sourcePath)
            self.dialog.dispose()
            return options.showDialog()
        if destinationPath and destinationPath != self.path and os.path.exists(os.path.dirname(destinationPath)) and destinationPath.endswith(".json"):
            self.path = destinationPath
            self.saveAs(destinationPath)
            return self
        if self.autosave and self.path:
            folder = os.path.dirname(self.path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            self.save()
        return self
        
        
    def createDialog(self):
        if self.nonBlocking:
            self.dialog = NonBlockingGenericDialog(self.getTitle())
        else:
            self.dialog = GenericDialog(self.getTitle())
        for option in self.sortedList():
            if option.isSameRow():
                self.dialog.addToSameRow()
            option.addToDialog(self.dialog)
        if self.previewPlugin:            
            runner = PlugInFilterRunner(self.previewPlugin, self.command, str(self))
            self.dialog.addPreviewCheckbox(runner) 
            self.dialog.addDialogListener(self.previewPlugin)
        self.dialog.addCheckbox("save", self.autosave)
        if self.helpUrl:
            self.dialog.addHelp(self.helpUrl)
            self.dialog.addToSameRow()
        self.dialog.addButton("Reset", self)
        self.dialog.addToSameRow()
        self.dialog.addButton("Make Default", self)
        self.dialog.addFileField("Load from...", self.path, PATH_FIELD_COLUMNS)
        self.dialog.addFileField("Save as...", self.path, PATH_FIELD_COLUMNS)
    
    
    def sortedList(self):
        orderedOptions = sorted(self.elements.values(), key=lambda option: option.order)
        orderedKeys = [option.key for option in orderedOptions]
        sortedList = [self.elements[key] for key in orderedKeys]
        return sortedList
        
        
    def get(self, key):
        return self.elements[key]
    
    
    def value(self, key):
        return self.get(key).getValue()
        
        
    def convertedValue(self, key):
        return self.get(key).getConvertedValue()
    
    
    def setValue(self, key, value):
        self.get(key).value = value
   
       
    def actionPerformed(self, e):
        command = e.getActionCommand()
        if not command in ["Reset", "Make Default"]:
            return
        if command == "Reset":
            self.resetToDefault()
            self.updateDialog()
        if command == "Make Default":
            self.makeDefault()       
        if command == "Browse":
            print("Browsing...")
        
   
    def resetToDefault(self):
        for option in self.elements.values():
            option.reset()
    
    
    def makeDefault(self):
        for option in self.elements.values():
            option.makeDefault()
    
    
    def updateDialog(self):
        for option in self.sortedList():
            option.updateDialog()
     
    
    def transferTo(self, client, aMapping):
        for key, value in aMapping.items():
            rsetattr(client, key, self.convertedValue(value))
        
    
    def getOptionsRepr(self):
        optionsString = ""
        options = self.sortedList()
        for option in options:
            optionsString = optionsString + option.key + "=" + str(option.value)
            if not option == options[-1]:
                optionsString = optionsString + ", "
        return optionsString
        
    
    def getOptionsStr(self):
        optionsString = ""
        options = self.sortedList()
        for option in options:
            optionsString = optionsString + option.label + ": " + str(option.value) + "\n"
        return optionsString
    
    
    def recordAndReport(self, command, img):
        self.report()
        self.record(command, img)
            
    
    def report(self):
        IJ.log(self.getOptionsStr())
    
    
    def record(self, command, img):
        macro = img.getProp("mri-cia.macro")
        if not macro:
            macro = ""
        else:
            macro = macro + "\n"
        command = 'run("' + command + '", "' + self.getOptionsRepr() + '");'        
        macro = macro + command
        img.setProp("mri-cia.macro", macro)
    
    
    def __str__(self):
        return self.__repr__()
    
    
    def __repr__(self):
        reprString = u"" + self.__class__.__name__ + "(" + self.getOptionsRepr() + ")"
        reprString = reprString.encode('ascii',errors='ignore')
        return reprString
        
        
    @classmethod
    def fromDict(cls, aDict):
        options = Options(aDict['title'])
        options.setHelpUrl(aDict['helpUrl'])
        if 'nonBlocking' in aDict.keys():
            options.nonBlocking = aDict['nonBlocking']
        elements = aDict['elements']
        for optionDict in elements.values():
            option = Option.fromDict(optionDict)
            options.add(option)
            option.order = optionDict['order']
        return options
     
     
    @classmethod
    def fromFile(cls, path):
        with open(path) as json_file:
            data = json.load(json_file)
        options = cls.fromDict(data)
        options.path = path
        return options



class Option(object):
    
   
    def __init__(self, key, value):
        super(Option, self).__init__()
        self.key = key
        self.value = value
        self.label = ""
        self.defaultValue = None
        self.order = 0
        self.helpText = ""
        self.type = "string"
        self.conversions = None
        self.field = None
        self.sameRow = False
        

    @classmethod
    def getTypes(cls):
        types = {'int': IntOption, 'float': FloatOption, 
             'string': StringOption, 'bool': BooleanOption, 
             'choice': ChoiceOption, 'image-choice': ImageChoiceOption,
             'directory': DirectoryOption}
        return types
    
    
    def getKey(self):
        return self.key


    def getValue(self):
        return self.value
        
        
    def getConvertedValue(self):
        return self.getValue()
    
    
    def setLabel(self, label):
        self.label = label


    def setDefaultValue(self, defaultValue):
        self.defaultValue = defaultValue


    def setOrder(self, order):
        self.order = order


    def setHelpText(self, text):
        self.helpText = text
        

    def asDict(self):
        "Answer public data attributes, private attributes starting with __ in the code will start with _ because of python name mangling."
        return {k: v for k, v in vars(self).items() if not k in ['field']}
    
    
    def addToDialog(self, dialog):
        dialog.addStringField(self.label, self.value)
        self.field = dialog.getStringFields()[-1]
        self.field.setName(self.key)
   
   
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextString()
   
   
    def getConvertedValue(self):       
        if not self.conversions:
            return self.value
        convertedValue = self.conversions[self.getValue()]
        return convertedValue
        
    
    def reset(self):
        self.value = self.defaultValue
    
    
    def makeDefault(self):
        self.defaultValue = self.value
    
    
    def updateDialog(self):
        self.field.setText(str(self.value))
        
        
    def getField(self):
        return self.field
    
    
    def isSameRow(self):
        return self.sameRow
    
        
    def __str__(self):
        return self.__repr__()
    
    
    def __repr__(self):
        reprString = u"" + self.__class__.__name__ + "(" + str(self.key) + ", " + str(self.value) + ")"
        reprString = reprString.encode('ascii',errors='ignore')
        return reprString
        
        
    @classmethod    
    def fromDict(cls, aDict):        
        option = cls.getTypes()[aDict['type']](aDict['key'], aDict['value'])
        for key, value in aDict.items():
            setattr(option, key, value)
        return option
        


class NumericOption(Option):


    def __init__(self, key, value):
        super(NumericOption, self).__init__(key, value)
        self.type = 'float'
    
        
    def addToDialog(self, dialog):
        dialog.addNumericField(self.label, self.value)
        self.field = dialog.getNumericFields()[-1]
        self.field.setName(self.key)
        

    def setValueFromDialog(self, dialog):
        self.value = float(dialog.getNextNumber())



class IntOption(NumericOption):


    def __init__(self, key, value):
        super(IntOption, self).__init__(key, value)
        self.type = 'int'
    
    
    def setValueFromDialog(self, dialog):
        self.value = int(dialog.getNextNumber())



class FloatOption(NumericOption):


    def __init__(self, key, value):
        super(FloatOption, self).__init__(key, value)
        self.type = 'float'



class StringOption(Option):

    
    def __init__(self, key, value):
        super(StringOption, self).__init__(key, value)
        self.type = 'string'
    
    
    def addToDialog(self, dialog):
        dialog.addStringField(self.label, self.value)
        self.field = dialog.getStringFields()[-1]
        self.field.setName(self.key)
    
    
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextString()

        
        
class BooleanOption(Option):


    def __init__(self, key, value):
        super(BooleanOption, self).__init__(key, value)
        self.type = 'bool'


    def addToDialog(self, dialog):
        dialog.addCheckbox(self.label, self.value)
        self.field = dialog.getCheckboxes()[-1]
        self.field.setName(self.key)
        

    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextBoolean()


    def updateDialog(self):
         self.field.setState(self.value)



class ChoiceOption(Option):


    def __init__(self, key, value):
        super(ChoiceOption, self).__init__(key, value)
        self.type = 'choice'
        self.choices = []


    def addToDialog(self, dialog):
        dialog.addChoice(self.label, self.choices, self.value)
        self.field = dialog.getChoices()[-1]
        self.field.setName(self.key)
        
        
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextChoice()
        
         
    def updateDialog(self):
        self.field.select(self.value)
    


class ImageChoiceOption(Option):


    def __init__(self, key, value):
        super(ImageChoiceOption, self).__init__(key, value)
        self.type = 'image-choice'


    def addToDialog(self, dialog):
        imageTitles = list(WindowManager.getImageTitles())
        images = ["None"] + imageTitles
        if not self.value in imageTitles:
            self.value = None
        dialog.addChoice(self.label, images, self.value)
        self.field = dialog.getChoices()[-1]
        self.field.setName(self.key)
        

    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextChoice()
        if self.value == "None":
            self.value = None


    def updateDialog(self):
        value = self.value
        if not value:
            value = "None"
        self.field.select(value)
       
       
        
class DirectoryOption(Option):

    
    def __init__(self, key, value):
        super(DirectoryOption, self).__init__(key, value)
        self.type = 'directory'
    
    
    def addToDialog(self, dialog):            
        dialog.addDirectoryField(self.label, self.value, PATH_FIELD_COLUMNS)
        self.field = dialog.getStringFields()[-1]
        self.field.setName(self.key)
    
    
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextString()
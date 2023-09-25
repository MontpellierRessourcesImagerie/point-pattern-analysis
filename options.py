import os
import json
from ij import WindowManager
from ij.gui import GenericDialog



class Options(object):


    def __init__(self, title):
        super(Options, self).__init__()
        self.title = title
        self.elements = {}
        self.helpUrl = ''
        
        self.dialog = None
        self.path = None
        self.autosave = True
        self.mappings = {}
        

    def setMapping(self, map, client):
        self.mappings[client] = map
    
    
    def getMapping(self, client):
        return self.mappings[client]   
    
    
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
        meAsDict = {'title': self.title, 'elements': optionsDict, 'helpUrl': self.helpUrl}
        return meAsDict
    
    
    def asJSON(self):
        data = json.dumps(self.asDict(), indent=4)
        return data
    
    
    def save(self):
        self.saveAs(self.path)
       
       
    def saveAs(self, path):
        with open(path, 'w') as outfile:
            outfile.write(self.asJSON())
       
    
    def showDialog(self):
        self.createDialog()
        self.dialog.showDialog()
        if self.dialog.wasCanceled():
            return False
        for option in self.sortedList():
            option.setValueFromDialog(self.dialog)
        self.autosave = self.dialog.getNextBoolean()
        if self.autosave and self.path:
            folder = os.path.dirname(self.path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            self.save()
        return True
        
        
    def createDialog(self):
        self.dialog = GenericDialog(self.getTitle())
        for option in self.sortedList():
            option.addToDialog(self.dialog)
        self.dialog.addCheckbox("save", self.autosave)
        if self.helpUrl:
            self.dialog.addHelp(self.helpUrl)
    
    
    def sortedList(self):
        orderedOptions = sorted(self.elements.values(), key=lambda option: option.order)
        return orderedOptions
        
    
    def get(self, key):
        return self.elements[key]
    
    
    def value(self, key):
        return self.get(key).getValue()
        
        
    def convertedValue(self, key):
        return self.get(key).getConvertedValue()
    
    
    def setValue(self, key, value):
        self.get(key).value = value
   
   
    @classmethod
    def fromDict(cls, aDict):
        options = Options(aDict['title'])
        options.setHelpUrl(aDict['helpUrl'])
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
        return vars(self)
    
    
    def addToDialog(self, dialog):
        dialog.addStringField(self.label, self.value)
   
   
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextString()
   
   
    def getConvertedValue(self):       
        if not self.conversions:
            return self.value
        convertedValue = self.conversions[self.getValue()]
        return convertedValue
        
        
    def __str__(self):
        return self.__repr__()
    
    
    def __repr__(self):
        repr = self.__class__.__name__ + "(" + str(self.key) + ", " + str(self.value) + ")"
        return repr
        
        
    @classmethod    
    def fromDict(cls, aDict):
        types = {'int': IntOption, 'float': FloatOption, 
                 'string': StringOption, 'bool': BooleanOption, 
                 'choice': ChoiceOption, 'image-choice': ImageChoiceOption}
        option = types[aDict['type']](aDict['key'], aDict['value'])
        for key, value in aDict.items():
            setattr(option, key, value)
        return option
        


class NumericOption(Option):


    def __init__(self, key, value):
        super(NumericOption, self).__init__(key, value)
        self.type = 'float'
    
    
    def addToDialog(self, dialog):
        dialog.addNumericField(self.label, self.value)


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
        
    
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextString()

        
        
class BooleanOption(Option):


    def __init__(self, key, value):
        super(BooleanOption, self).__init__(key, value)
        self.type = 'bool'


    def addToDialog(self, dialog):
        dialog.addCheckbox(self.label, self.value)
        

    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextBoolean()



class ChoiceOption(Option):


    def __init__(self, key, value):
        super(ChoiceOption, self).__init__(key, value)
        self.type = 'choice'
        self.choices = []


    def addToDialog(self, dialog):
        dialog.addChoice(self.label, self.choices, self.value)
        
        
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextChoice()
        
          
           
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
        
        
    def setValueFromDialog(self, dialog):
        self.value = dialog.getNextChoice()
        if self.value == "None":
            self.value = None

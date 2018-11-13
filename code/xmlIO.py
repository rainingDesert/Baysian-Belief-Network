import xml.sax as xs
import copy
import gc

class LoadCPT(xs.ContentHandler):
    # initialization function
    def __init__(self):
        self.currentTag = None      # store current tage name
        self.attrs = {}             # store attributes {attr: type, outcome}
        self.type = None            # store type of current VARIABLE
        self.name = None            # store name of current VARIABLE or node
        self.tableName = None       # name of table

        self.CPT = {}               # CPT {node: [[parents], [children], [value]]}
    
    # start of each element
    def startElement(self, tag, attributes):
        self.currentTag = tag
        if(tag == "VARIABLE"):
            self.type = attributes["TYPE"]

    # end of each element
    def endElement(self, tag):
        self.currentTag = " "
    
    # trigger
    def characters(self, content):
        #-------inside VARIABLE-------
        # name label
        if(self.currentTag == "NAME"):
            #table name
            if(self.tableName == None):
                self.tableName = content
            #attribute name
            else:
                self.name = content
                self.attrs[content] = [self.type]

        # outcome label / type of attribute
        if(self.currentTag == "OUTCOME"):
            self.attrs[self.name].append(content)

        #------inside DEFINITION-------
        # FOR label / node attribute
        if(self.currentTag == "FOR"):
            self.name = content
            # content already in CPT
            if(content not in self.CPT):
                self.CPT[content] = [[], [], []]
        
        # GIVEN label / parent attribute
        if(self.currentTag == "GIVEN"):
            # parent must in CPT
            if(content not in self.CPT):
                self.CPT[content] = [[], [], []]
            self.CPT[self.name][0].append(content)
            self.CPT[content][1].append(self.name)
        
        # TABLE label / CPT value
        if(self.currentTag == "TABLE"):
            # id follows certain order
            if(len(content) != 0):
                self.CPT[self.name][2] += [float(num) for num in content.split()]

class GetCPT:
    # initialization function
    def __init__(self, fileName):
        self.attrs = None   # store attributes {attr: type, outcome}
        self.CPT = None     # CPT {node: [[parents], [children], [value]]}
        self.tableName = None # name of table        
        self.__getCPT(fileName)

    # get CPT from file
    def __getCPT(self, fileName):
        #create XMLReader
        parser = xs.make_parser()
        #turn off namespaces
        parser.setFeature(xs.handler.feature_namespaces, 0)

        #rewrite
        handler = LoadCPT()
        parser.setContentHandler(handler)
        
        #get CPT
        parser.parse(fileName)
        self.attrs = copy.deepcopy(handler.attrs)
        self.CPT = copy.deepcopy(handler.CPT)
        self.tableName = copy.deepcopy(handler.tableName)

        #delete objects
        del handler.attrs
        del handler.CPT
        del handler
        del parser
        gc.collect()

if(__name__ == "__main__"):
    handler = GetCPT("./examples/aima-wet-grass.xml")

    print(handler.tableName)
    print("---------------------------")
    print(handler.attrs)
    print("---------------------------")
    print(handler.CPT)

    
import xmlIO
import copy
import gc

# enumeration algorithm
class Enumeration:
    # init functin
    def __init__(self):
        self.CPTStore = {}

    # implement enumeration
    def __enumerationAll(self, CPTAttr, evidence):
        # already end
        if(len(CPTAttr) == 0):
            return 1.0

        # get the first attribute
        curCPTAttr = copy.deepcopy(CPTAttr)
        attr = curCPTAttr.pop(0)

        # multiple if in evidence
        if(attr in evidence):
            return self.CPTStore.getProbability(attr, evidence) * self.__enumerationAll(curCPTAttr, evidence)
        # sum if hidden attribute
        else:
            totValue = 0.0
            newEvidence = copy.deepcopy(evidence)
            for valueId in range(len(self.CPTStore.attrs[attr]) - 1):
                newEvidence[attr] = valueId
                totValue += self.CPTStore.getProbability(attr, newEvidence) * self.__enumerationAll(curCPTAttr, newEvidence)

            del newEvidence
            return totValue

    # start enumeration algorithm
    # query: string (attribute name)
    # evidence: dict ({attribute name: valueId})
    def enumerationAsk(self, query, evidence, CPT):
        # get CPT
        self.CPTStore = CPT

        # get CPT attribute order
        CPTvars = self.CPTStore.orderAttrCPT()

        # calculate value of query attribute
        queryRes = []
        newEvidence = copy.deepcopy(evidence)
        for valueId in range(len(self.CPTStore.attrs[query]) - 1):
            newEvidence[query] = valueId
            queryRes.append(self.__enumerationAll(CPTvars, newEvidence))
        
        #normalize result
        normalRes = [res / sum(queryRes) for res in queryRes]

        #delete
        del newEvidence
        gc.collect()

        return normalRes

# variable elimination
class valueElimination:
    # init function
    def __init__(self):
        pass

    # order attributes according to size of next factor
    def __orderVars(self, attrs, evidence, factorNames, CPT):
        attrList = [[attrFactor for attrFactor in copy.deepcopy(factorNames) if attrFactor not in evidence] for attr in attrs]

        # attributes in currrent factors
        for attrId, attr in enumerate(attrs):
            if(attr in attrList[attrId]):
                attrList.pop(attrList.idnex(attr))

        # attributes not calculated yet
        for attrId, attr in enumerate(attrs):
            # parent
            check = True
            for candidate in CPT.CPT[attr][0]:
                if(candidate not in attrs):
                    check = False
                    break

            if(check):
                attrList[attrId] += [candidate for candidate in CPT.CPT[attr][0] if candidate not in evidence]

            # children
            for candidate in CPT.CPT[attr][1]:
                # child has been selected
                if(candidate not in attrs):
                    continue
                
                #child connects only current attribute
                if(len(CPT.CPT[candidate][0]) == 1):
                    continue

                # parents of children
                check = True
                for parCan in CPT.CPT[candidate][0]:
                    if(parCan not in attrs):
                        check = False
                        break
                if(check):
                    attrList[attrId] += [node for node in CPT.CPT[candidate][0] if node not in evidence and node != attr]
        
        # get dimension
        attrDim = [len(set(attrSet)) for attrSet in attrList]
        
        # select the one with least dimension
        return attrs[attrDim.index(min(attrDim))]


    # build new factors
    def __newFactors(self, curAttr, attrs, evidence, CPT, pastFactorNames, pastFactors):
        newFactors = []     # new factors
        newFactorNames = []     # name for new factors

        # parents
        check = True
        for candidate in CPT.CPT[curAttr][0]:
            if(candidate not in attrs):
                check = False
                break
        
        if(check):
            newFactorNames.append([candidate for candidate in CPT.CPT[curAttr][0] + [curAttr] if(candidate not in evidence)])
            newFactors.append(CPT.getFactor(curAttr, evidence))

        # children
        for candidate in CPT.CPT[curAttr][1]:
            # child has been selected
            if(candidate not in attrs):
                continue
            
            # child connect only current attribute
            if(len(CPT.CPT[candidate][0]) == 1):
                continue

            # parent of child
            check = True
            for parCan in CPT.CPT[candidate][0]:
                if(parCan not in attrs):
                    check = False
                    break
            if(check):
                newFactorNames.append([parCan for parCan in CPT.CPT[candidate][0] if parCan not in evidence] + [candidate])
                newFactors.append(CPT.getFactor(candidate, evidence))
        
        # mutiple
        newFactorNames.append(pastFactorNames)
        newFactors.append(pastFactors)
        
        factorNames = [newFactorNames[0]]
        factors = [newFactors[0]]
        for newNameList in newFactorNames[1:]:
            # merge name
            tempFactorNames = factorNames + [name for name in newNameList if name not in factorNames]

            # get factors
            tempFactors = []
            for factorId in range(sum([len(CPT.attr[name]) - 1 for name in tempFactorNames])):

                # calculate result
                rows = [0, 0]
                tempFactorId = factorId
                for nameId in range(len(tempFactorNames) - 1, -1, -1):
                    tempFactorName = tempFactorNames[nameId]
                    value = tempFactorId % (len(CPT.attr[tempFactorName]) - 1)
                    tempFactorId = tempFactorId // (len(CPT.attr[tempFactorName]) - 1)
                    if(value != 0):

                        # update row of the first factor
                        if(tempFactorName in factorNames):
                            baseList = [len(CPT.attr[factorNames[bit]]) - 1 for bit in range(len(factorNames) - 1, factorNames.index(tempFactorName), -1)]
                            if(len(baseList) == 0):
                                base = 1
                            else:
                                base = sum(baseList)
                            rows[0] += value * base

                        # update row of the second factor
                        if(tempFactorName in newNameList):
                            baseList = [len(CPT.attr[newNameList[bit]]) - 1 for bit in range(len(newNameList) - 1, newNameList.index(tempFactorName), -1)]
                            if(len(baseList) == 0):
                                base = 1
                            else:
                                base = sum(baseList)
                            rows[1] += value * base

                # update factor
                tempFactors.append(factorNames[rows[0]] * newNameList[rows[1]])

            # new factor
            factorNames = tempFactorNames
            factors = tempFactors

        return factorNames, factors

    # sum up factors
    def __sumFactors(self, attr, factors, factorNames):
        return None

    # do elimination
    # query: string (attribute name)
    # evidence: dict ({attribute name: valueId})
    def enumerationAsk(self, query, evidence, CPT):
        factors = []       # store factor: []
        factorNames = []    # variable included in the factor
        attrs = list(CPT.attrs.keys())    #attributes: [attr, ...]
        newEvidence = copy.deepcopy(evidence)   #evidence
        
        while(len(attrs) != 0):
            # select an attribute to be eliminated
            curAttr = self.__orderVars(attrs, newEvidence, factorNames, CPT)

            # update factors (mutiple)
            factorNames, factors = self.__newFactors(curAttr, attrs, newEvidence, CPT, factorNames, factors)

            # update factors (sum)
            if(curAttr not in evidence and curAttr != query):
                self.__sumFactors(curAttr, factors, factorNames)

            # drop current attribute
            attrs.pop(attrs.index(curAttr))
        
        # normalize final factors
        result = [p / sum(factors[0]) for p in factors[0]]

        # delete
        del newEvidence
        gc.collect()

        return result
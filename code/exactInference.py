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
    def __orderVars(self, attrs, evidence, CPT):
        attrList = [[] for attr in attrs]

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
                
                # parents of children
                check = True
                for parCan in CPT.CPT[candidate][0]:
                    if(parCan not in attrs):
                        check = False
                        break
                if(check):
                    attrList[attrId] += [node for node in CPT.CPT[candidate][0] if(node not in evidence and node != attr)]
        
        # get dimension
        attrDim = [len(set(attrSet)) for attrSet in attrList]
        
        # select the one with least dimension
        return sorted(attrs, key = lambda k : attrDim[attrs.index(k)] )

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

            # parent of child
            check = True
            for parCan in CPT.CPT[candidate][0]:
                if(parCan not in attrs):
                    check = False
                    break
            if(check):
                newFactorNames.append([parCan for parCan in CPT.CPT[candidate][0] + [candidate] if(parCan not in evidence)])
                newFactors.append(CPT.getFactor(candidate, evidence))
        
        # mutiple
        if(len(pastFactorNames) != 0):
            newFactorNames.append(pastFactorNames)
            newFactors.append(pastFactors)

        factorNames = copy.deepcopy(newFactorNames[0])
        factors = copy.deepcopy(newFactors[0])
        for newNameList, newFactorList in zip(newFactorNames[1:], newFactors[1:]):
            # merge name
            tempFactorNames = factorNames + [name for name in newNameList if name not in factorNames]

            # get factors
            tempFactors = []
            commentNames = [[nameId, newNameList.index(name)] for nameId, name in enumerate(factorNames) if name in newNameList]
            for factor in factors:
                for newFactor in newFactorList:
                    check = True
                    for names in commentNames:
                        if(factor[0][names[0]] != newFactor[0][names[1]]):
                            check = False
                            break
                    if(check):
                        tempFactorAttrs = copy.deepcopy(factor[0])
                        tempFactorAttrs += [attrVal for attrValId, attrVal in enumerate(newFactor[0]) if(newNameList[attrValId] not in factorNames)]
                        tempFactors.append([tempFactorAttrs, factor[1] * newFactor[1]])

            # new factor
            factorNames = tempFactorNames
            factors = tempFactors

        return factorNames, factors

    # sum up factors
    def __sumFactors(self, attr, factors, factorNames, CPT):
        attrId = factorNames.index(attr)
        tempFactors = copy.deepcopy(factors)

        # get rows and sum
        # calculate merge distance
        disId = 1
        for nameId in range(len(factorNames) - 1, attrId, -1):
            disId *= len(CPT.attrs[factorNames[nameId]]) - 1
        
        # merge factor
        newFactorNames = copy.deepcopy(factorNames)
        newFactorNames.pop(attrId)

        newFactors = []
        attrValueNum = len(CPT.attrs[attr]) - 1

        # bits up to current ID
        upNum = 1
        for nameId in range(attrId):
            upNum *= len(CPT.attrs[factorNames[nameId]]) - 1
        for upId in range(upNum):
            for downId in range(disId):
                newFactor = [[], 0]

                newFactor[1] = sum([tempFactors[upId * disId * attrValueNum + num * disId + downId][1] for num in range(attrValueNum)])
                newFactor[0] = copy.deepcopy(tempFactors[upId * disId * attrValueNum + downId][0])
                newFactor[0].pop(attrId)
                newFactors.append(newFactor)
        
        return newFactorNames, newFactors

    # do elimination
    # query: string (attribute name)
    # evidence: dict ({attribute name: valueId})
    def enumerationAsk(self, query, evidence, CPT):
        factors = []       # store factor: [[[attribute value, ...], value], ...]
        factorNames = []    # variable included in the factor
        newEvidence = copy.deepcopy(evidence)   #evidence
        attrs = self.__orderVars(list(CPT.attrs.keys()), newEvidence, CPT) #attributes: [attr, ...]

        while(len(attrs) != 0):
            # select an attribute to be eliminated
            curAttr = attrs[0]

            # update factors (mutiple)
            factorNames, factors = self.__newFactors(curAttr, attrs, newEvidence, CPT, factorNames, factors)

            # update factors (sum)
            if(curAttr not in evidence and curAttr != query):
                factorNames, factors = self.__sumFactors(curAttr, factors, factorNames, CPT)

            # drop current attribute
            attrs.pop(0)
        
        # normalize final factors
        result = [factor[1] for factor in factors]
        result = [p / sum(result) for p in result]

        # delete
        del newEvidence
        gc.collect()

        return result
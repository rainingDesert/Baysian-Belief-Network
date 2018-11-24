import xmlIO
import random
import copy
import gc
import threading
import math
import exactInference

# inherit threading
class MyThread(threading.Thread):
    # initial function
    def __init__(self, sampleFun, args = ()):
        super(MyThread, self).__init__()
        self.sampleFun = sampleFun
        self.args = args
        self.result = None

    # implementation
    def run(self):
        self.result = self.sampleFun(*self.args)

class Sampling:
    #initial function
    def __init__(self):
        pass

    # random sample
    def __randomSample(self, CPT, evidence, var):
        newEvidence = copy.deepcopy(evidence)
        probs = []
        # get probability
        for valueId in range(len(CPT.attrs[var]) - 1):
            newEvidence[var] = valueId
            probs.append(CPT.getProbability(var, newEvidence))
    
        # do sample
        result = random.random()
        for valueId, prob in enumerate(probs):
            if(prob >= result):
                
                # delete
                del newEvidence
                del probs
                gc.collect()
                
                return valueId
            result -= prob

        print("Error here")
        return -1

    # random sample with Markov Blanket
    def __marBlanSample(self, CPT, evidence, var, exInf):
        # get probability
        newEvidence = copy.deepcopy(evidence)
        probs = exInf.enumerationAsk(var, newEvidence, CPT)

        # do sample
        result = random.random()
        for valueId, prob in enumerate(probs):
            if(prob >= result):
                
                # delete
                del newEvidence
                del probs
                gc.collect()
                
                return valueId
            result -= prob

        print("Error here")
        return -1

    # sample for rejection sampling
    def __priorSample(self, CPT):
        # get attribute list
        CPTvars = CPT.orderAttrCPT()
        evidence = {}

        # sample
        for var in CPTvars:
            # random sample for var
            evidence[var] = self.__randomSample(CPT, copy.deepcopy(evidence), var)

        return evidence

    # sample for likelihood weighting
    def __weightedSample(self, CPT, evidence):
        weight = 1.0      # initial weight
        CPTvars = CPT.orderAttrCPT()    # list of attributes
        sampleEvidence = {}     # sample values

        # sample
        for var in CPTvars:
            # an evidence attribute
            if(var in evidence):
                sampleEvidence[var] = evidence[var]
                weight *= CPT.getProbability(var, sampleEvidence)
            
            # random sample
            else:
                sampleEvidence[var] = self.__randomSample(CPT, sampleEvidence, var)
        
        return sampleEvidence, weight

    # rejection sampling
    # query: string
    # evidence: dict ({attribute name: valueId})
    # sampleNum: integer
    def __rejectSample(self, query, evidence, CPT, sampleNum):

        # number of query
        queryNum = [0 for value in range(len(CPT.attrs[query]) - 1)]

        # each sampling
        for i in range(sampleNum):
            sampleRes = self.__priorSample(CPT)

            # match evidence
            check = True
            for resAttr in sampleRes:
                # not match
                if(resAttr in evidence and sampleRes[resAttr] != evidence[resAttr]):
                    check = False
                    break
            # if match
            if(check):
                queryNum[sampleRes[query]] += 1
        
        return queryNum

    # likelihood weighting
    def __likelihoodWeight(self, query, evidence, CPT, sampleNum):
        
        # weight of query
        queryWeight = [0 for value in range(len(CPT.attrs[query]) - 1)]

        #do sampling
        for i in range(sampleNum):
            sampleRes, weight = self.__weightedSample(CPT, evidence)
            
            # update weight
            queryWeight[sampleRes[query]] += weight

        return queryWeight

    # gibbs sampling
    def __gibbsSample(self, query, evidence, CPT, sampleNum):
        # exact inference object
        exInf = exactInference.Enumeration()
        queryRes = [0 for value in range(len(CPT.attrs[query]) - 1)]

        # get attributes in CPT
        nonEviVars = [var for var in list(CPT.attrs.keys()) if(var not in evidence)]
        varMarBlan = [CPT.getMarBlan(var) for var in nonEviVars]

        # initialize values for attributes
        state = {var : random.randint(0, len(CPT.attrs[var]) - 2) for var in list(CPT.attrs.keys())}
        for attr in evidence:
            state[attr] = evidence[attr]

        # sample
        for i in range(sampleNum):
            # sample each attribute
            for varId, var in enumerate(nonEviVars):
                # set value for Markov Blanket
                newEvidence = {marVar : state[marVar] for marVar in varMarBlan[varId]}
                # random sample
                result = self.__marBlanSample(CPT, newEvidence, var, exInf)
                # update sample result
                state[var] = result
                queryRes[state[query]] += 1

        # delete
        del exInf
        del nonEviVars
        del varMarBlan
        del state
        gc.collect()

        return queryRes

    # call from outside for rejection sampling
    def callRejectSample(self, query, evidence, CPT, sampleNum, threadNum = 5):

        # thread number too much
        if(threadNum > sampleNum):
            threadNum = sampleNum

        # result list
        queryNum = []

        # create threads
        threads = [MyThread(self.__rejectSample, args = (query, evidence, CPT, math.ceil(sampleNum / threadNum))) for threadId in range(threadNum)]
        
        # start thread
        for thread in threads:
            thread.start()

        # join thread and get result
        for thread in threads:
            thread.join()
            queryNum.append(thread.result)
        
        # normalize
        quertResult = [0 for i in queryNum[0]]
        for subQuery in queryNum:
            quertResult = [quertResult[valueId] + subQuery[valueId] for valueId in range(len(subQuery))]

        print("number of useful sample points is " + str(sum(quertResult)))

       # not enough sample
        if(sum(quertResult) == 0):
            print("no sampling point may due to not enough sampling number or rare evidence")
            return None

        quertResult = [value / sum(quertResult) for value in quertResult]
        return quertResult

    # call from outside for likelihood sampling
    def callLikelihood(self, query, evidence, CPT, sampleNum):
        queryWeight = self.__likelihoodWeight(query, evidence, CPT, sampleNum)

        # normalization
        queryWeight = [weight / sum(queryWeight) for weight in queryWeight]

        return queryWeight

    # call from outsider for gibbs sampling
    def callGibbsSample(self, query, evidence, CPT, sampleNum):
        queryRes = self.__gibbsSample(query, evidence, CPT, sampleNum)

        # normalization
        queryRes = [res / sum(queryRes) for res in queryRes]

        return queryRes
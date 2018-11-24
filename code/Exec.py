import gc
import sys
import xmlIO
import exactInference
import approximate
import time

class Execution:
    # initialize function
    def __init__(self):
        self.method = None
        self.CPTStore = None
        self.query = ""
        self.sampleNum = 0
        self.evidence = {}
        self.__getArgument()

    # get argument
    def __getArgument(self):
        # start number of file
        start = 0

        # check method
        self.method = sys.argv[-1]
        if(self.method == "enum" or self.method == "elim"):
            start = 1
        else:
            self.sampleNum = int(sys.argv[1])
            start = 2

        # check file name
        fileName = sys.argv[start]
        if(fileName == "test"):
            start += 1
            fileName = int(sys.argv[start])
        
        self.query = sys.argv[start + 1]
        self.evidence = {sys.argv[argvId]:sys.argv[argvId + 1].lower() for argvId in range(start + 2, len(sys.argv) - 1, 2)}

        # load CPT
        self.CPTStore = xmlIO.GetCPT(fileName)

        # update evidence
        self.evidence = {attr: self.CPTStore.attrs[attr].index(self.evidence[attr]) - 1 for attr in self.evidence}

    # execute inference (Enumeration)
    def execInfEnum(self):
        # call Enumeration
        enum = exactInference.Enumeration()

        start = time.time()
        result = enum.enumerationAsk(self.query, self.evidence, self.CPTStore)
        end = time.time()

        print("time consuming is " + str(end - start) + " second")

        print("probability used count is : " + str(self.CPTStore.count))

        # delete
        del enum
        gc.collect()

        result = [round(p, 3) for p in result]
        return result

    # execute inference (Variable Elimination)
    def execVarElim(self):
        # call Enumeration
        enum = exactInference.valueElimination()

        start = time.time()
        result = enum.enumerationAsk(self.query, self.evidence, self.CPTStore)
        end = time.time()

        print("time consuming is " + str(end - start) + " second")

        print("probability used count is : " + str(self.CPTStore.count))

        # delete
        del enum
        gc.collect()

        result = [round(p, 3) for p in result]
        return result

    # execute rejection sampling
    def execRejSample(self):
        # call approximate inference: rejection sampling
        rej = approximate.Sampling()

        start = time.time()
        result = rej.callRejectSample(self.query, self.evidence, self.CPTStore, self.sampleNum, 1)
        end = time.time()

        print("time consuming is " + str(end - start) + " second")

        # delete
        del rej
        gc.collect()

        if(result == None):
            return result

        result = [round(p, 3) for p in result]
        return result

    # execute likelihood weighting 
    def execWeightSample(self):
        # call approximate inference: likelihood weighting
        wei = approximate.Sampling()

        start = time.time()
        result = wei.callLikelihood(self.query, self.evidence, self.CPTStore, self.sampleNum)
        end = time.time()

        print("time consuming is " + str(end - start) + " second")

        # delete
        del wei
        gc.collect()

        result = [round(p, 3) for p in result]
        return result

    # execute gibbs sampling
    def execGibbsSample(self):
        # call approximate inference: gibbs sampling
        gib = approximate.Sampling()

        start = time.time()
        result = gib.callGibbsSample(self.query, self.evidence, self.CPTStore, self.sampleNum)
        end = time.time()

        print("time consuming is " + str(end - start) + " second")

        # delete
        del gib
        gc.collect()

        result = [round(p, 3) for p in result]
        return result

# normal execution
def norExec():
    ex = Execution()
    norm = None

    # exact inference with enumeration
    if(ex.method == "enum"):
        print("Exact inference with enumeraton: ")
        norm = ex.execInfEnum()

    # approximate inference with 
    elif(ex.method == "elim"):
        print("Exact inference with Validation ELimination: ")
        norm = ex.execVarElim()

    # approximate inference with rejection sampling
    elif(ex.method == "rej"):
        print("Approximate inference with rejection sampling: ")
        norm = ex.execRejSample()

    # approximate inference with likelihood weighting
    elif(ex.method == "wei"):
        print("Approximate inference with likelihood weighting: ")
        norm = ex.execWeightSample()

    # approximate inference with gibbs sampling
    elif(ex.method == "gib"):
        print("Approximate inference with Gibbs Sampling: ")
        norm = ex.execGibbsSample()

    # error message
    else:
        print("unrealizable message with " + ex.method)
        print("--------------function-----------------")
        print("enum: enumeration")
        print("elim: validation elimination")
        print("rej: rejection sampling")
        print("wei: likelihood weighting")
        print("gib: Gibbs sampling")
        exit(1)

    print("result is: ", end = " ")
    print(norm)

if(__name__ == "__main__"):
    norExec()
import settings as SETTINGS
import sys
import time
products = []
basket = []
zipped_basket = []
SUPPORT = SETTINGS.MIN_SUPPORT
CONFIDENCE = SETTINGS.MIN_CONFIDENCE
MIN_SUPPORT_NUMERICAL = 0
support_dict = {}
def main():
    start_time = time.time()
    print "Support: %s\nConfidence:%s\n"%(SUPPORT, CONFIDENCE)
    global basket
    global zipped_basket
    global products
    global MIN_SUPPORT_NUMERICAL
    global support_dict
    global outfile
    products_file = open("products")
    outfile=open("outfile", "w")
    
    for line in products_file:
        products.append(line.split(',',1)[0])
    
    basket_file = open("small_basket.dat")
    for line in basket_file:
        temp=[]
        line = line.strip()
        line = line.split(', ')[1:]
        for index,number in enumerate(line):
            if (int(number)!=0):
                temp.append(index)
        basket.append(temp)
    
    basket = map(set, basket)
    global num_items
    num_items = float(len(basket))
    print "There are %s transactions" %num_items
    print "There are %s products" %len(products)
    MIN_SUPPORT_NUMERICAL = SUPPORT*num_items

    c1 = createC1()
    Lk, support_dict = scanBasket(c1)
    newLk=Lk
    k=2

    while len(newLk) is not 0:
        print "K=%s: %s"%(k-1, len(newLk))
        Lk=list(newLk)
        CKplus1=createCandidates(Lk,k)
        if not CKplus1:
            break
        newLk,support_dict=scanBasket(CKplus1)
        k+=1
    
    print "Generate rules with frequent itemset(s):", newLk
    
#     for i in newLk:
#         for j in i:
#             print products[j]
#         print "\n"
    
    generateRules(newLk, support_dict)

    print("--- %s seconds ---" % (time.time() - start_time))

def createC1():
    c1 = []
    for i in xrange(len(products)):
        c1.append([i])
    return map(set,c1)

def scanBasket(Ck):
    count={}
    Lk = []
    for tid in basket:
        for cand in Ck:
            if set(cand).issubset(set(tid)):
                count.setdefault(tuple(cand),0)
                count[tuple(cand)]+=1
    for key in count:
        if count[key]>=MIN_SUPPORT_NUMERICAL:
            Lk.append(key)
            support_dict[key]=count[key] #Keeps track of all supports
    return Lk, support_dict
       
def createCandidates(Lk, k):
    new_candidates = []
    Lk.sort()
    if len(Lk)==1:
        return None
    elif k is 2:
        for index,i in enumerate(Lk):
            for jindex in range(index,len(Lk)-1):
                j=Lk[jindex+1]
                new_item=set(i)|set(j)
                new_item=tuple(sorted(new_item))
                new_candidates.append(new_item)
    else:
        for index,i in enumerate(Lk):
            for jindex in range(index,len(Lk)-1):
                j=Lk[jindex+1]
                L1=i[:-1]
                L2=j[:-1]
                if L1==L2:
                    new_item=set(i)|set(j)
                    new_item=tuple(sorted(new_item))
                    new_candidates.append(new_item)
    
    pruned_new_candidates=prune(new_candidates, Lk, k-1)
    return pruned_new_candidates

def prune(candidates, freq_items, k):
    for i in candidates:
        possible_subsets = sys.modules['itertools'].combinations(i, k)
        for j in possible_subsets:
            j=set(j)
            if not j.issubset(i):
                candidates.remove(j)
    return candidates

def generateRules(Lk, support_dict):
    rules=[]
    if len(Lk) is 2:
        for consequent in Lk:
            calculateConfidence(Lk, [(consequent)], rules)
    else:
        for set_items in Lk:
            subsets=generateSubsets(set_items)
            getRules(set(set_items), subsets, rules)
            
def generateSubsets(set_items):
    x = sys.modules['itertools'].combinations(set_items, 1)
    newlist = []
    for i in x:
        newlist.append(set(i))
    return newlist

def getRules(superset, subsets, rules):
    superset = sorted(superset)
    subsets = sorted(subsets)
    
    for subset_item in subsets:
        consequent = subset_item
        if len(consequent) is 1:
            consequent = calculateConfidence(superset, subset_item, rules)
            if consequent is not None:
                generateRulesFromConsequent(superset, consequent, rules)
    printRules(rules)
    
def generateRulesFromConsequent(superset, consequent, rules):
    precedent = sorted(set(superset)-set(consequent))
    if len(precedent) is not 1:
        for prec in precedent:
            new_consequent = consequent[:]
            new_consequent.append(prec)
            new_consequent = calculateConfidence(superset, new_consequent, rules)
            if new_consequent is None:
                break
        
def calculateConfidence(superset, consequent, rules):
    precedent = sorted(set(superset)-set(consequent))
    precedent = sorted(precedent)
    consequent=sorted(consequent)
    superset = sorted(superset)
    calculated_confidence = float(support_dict[tuple(superset)])/support_dict[tuple(precedent)]
    if (calculated_confidence>=CONFIDENCE):
        set1=[]
        for product_index in precedent:
            product = products[product_index]
            set1.append(product)                        
        set2=[]
        for product_index in consequent:
            product = products[product_index]
            set2.append(product)

        lift_ratio = calculated_confidence/((support_dict[tuple(consequent)])/num_items)        
        rules.append([precedent, consequent, calculated_confidence, lift_ratio])
        return consequent
    
def printRules(rules):
    outfile.write("%s rules were generated:\n"%len(rules))
    print "%s rules were generated"%len(rules)
    for rule in rules:
        precedents = rule[0]
        consequents = rule[1]
        if not isinstance(rule[0][0], str):
            for index, i in enumerate(precedents):
                precedents[index] = str(products[int(i)])
                             
            for index, j in enumerate(consequents):
                consequents[index]= str(products[j])
        precedents_string = ', '.join(precedents)
        consequents_string = ', '.join(consequents)

        conf = rule[2]
        lift = rule[3]
        outfile.write("%s --> %s \nConfidence level: %s\nLift: %s\n\n"%(precedents_string,consequents_string, str(conf), str(lift)))
        print ("%s --> %s \nConfidence level: %s\nLift: %s\n"%(precedents_string,consequents_string, str(conf), str(lift)))
if __name__ == "__main__":
    main()

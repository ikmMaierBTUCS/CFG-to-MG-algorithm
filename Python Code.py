def cfg2mg(CFG):
    '''
    Converts a categorized CFG into an MG
    Input: Categorized CFG = List of of rules
    Rule = 3-tuple (Non-Terminal, Word, Category), 
    i.e. the Non-terminal can generate the word Word of category Category
    Capital letters are always interpretted as non-terminals here, minor letters as terminals.
    Words are strings out of terminals and non-terminals.
    Categories are strings that describe the type/category of a produced word.
    S is the default start symbol
    '''
    #for rule in CFG:
        #print(rule)
    CFG += [('START', 'S', 'cFin')]
    N = set([rule[0] for rule in CFG]) # Set of all NTs
    F = [] # Free NTs
    R = [] # Restricted NTs
    target_category = {} # Dictionary that stores the target category of each NT
    
    category_order = determine_partial_category_order(CFG)
    #print('Category order:')
    #print(category_order.relations)
    aux_NTs = []
    for NT in N:
        # adapt the grammar so that NT has one unique target category
        # and write this in the dictionary 'target_category'
        #copy_C = CFG[:]
        NT_rules = [rule for rule in CFG if rule[0] == NT]
        targetted_categories = [rule[2] for rule in NT_rules]
        if len(targetted_categories) > 1:
            main_category = category_order.maximum(targetted_categories)
            #print('main target category of '+NT+' is '+main_category)
            target_category[NT] = main_category
            updated_NT_rules = [rule for rule in NT_rules if rule[2] == main_category]
            secondary_categories = list(set(targetted_categories) - set([main_category])) 
            #print('secondary categries:')
            #print(secondary_categories)
            for ind in range(len(secondary_categories)):
                category_order.relations.add((main_category,secondary_categories[ind]))
                updated_NT_rules += [(NT, NT+str(ind), main_category)]
                target_category[NT+str(ind)] = secondary_categories[ind]
                aux_NTs += [NT+str(ind)]
                for rule in NT_rules:
                    if rule[2] == secondary_categories[ind]:
                        updated_NT_rules += [(NT+str(ind), rule[1], secondary_categories[ind])]
            #print('Updated rules:')
            #print(updated_NT_rules)
            CFG = [rule for rule in CFG if rule not in NT_rules] + updated_NT_rules
        else:
            target_category[NT] = targetted_categories[0]
        #print('Any changes to CFG?')
        #print(not copy_C == CFG)
        #print('Any changes to target categories?')
        #print(target_category)
        #print('Any changes to category order?')
        #print([rel for rel in category_order.relations])
        # decide if NT controls free input slots or restricted ones
        if free(NT,CFG):
            F += [NT]
        else:
            R += [NT]
    for n in aux_NTs:
        N.add(n)
        if free(n,CFG):
            F += [n]
        else:
            R += [n]
    #print('Free NTs:')
    #print(F)
    #print('Restricted NTs:')
    #print(R)
    #print('Target Categories:')
    #print(target_category)
    
    transformable_CFG = []
    for rule in CFG:
        # decompose each rule into rules that are transformable into MG items
        # it means that they may only have NTs at their first or last spot and they have to be one of the shapes
        # word, Rword, wordF or FwordF
        transformable_CFG += decompose_rule(rule,R,F,N,target_category)
    
    #for rule in transformable_CFG:
        #print(rule)
    #print('Free:')
    #print(F)    
    #print('Target Categories:')
    #print(target_category)

    summarized_tf_CFG = []
    for rule in transformable_CFG:
        same_rule_found = False
        for i in range(len(summarized_tf_CFG)):
            # check if 2 rules produce same string and category
            if rule[1].replace('*','') == summarized_tf_CFG[i][1].replace('*','') and rule[2] == summarized_tf_CFG[i][2]:
                same_rule_found = True
                # then: summarize them into one
                summarized_tf_CFG[i][0] += [rule[0]]
        if not same_rule_found:
            # otherwise: add new rule
            summarized_tf_CFG += [[[rule[0]],rule[1],rule[2]]]
    #print('summarized transformed CFG:')
    #for rule in summarized_tf_CFG:
        #print(rule)
    
    MG_without_licensors = []
    for rule in summarized_tf_CFG:
        # create a proper MG item
        # created as a 3-tuple, so in the 2nd and 3rd entry information can be stored, based on which licensors are assigned later
        #print('model:')
        #print(rule)
        chars = list(rule[1])
        for char in reversed(range(len(chars))):
            if chars[char][0] == '*' or chars[char][0].isnumeric() or chars[char][0] == '+':
                chars = chars[:char - 1] + [chars[char - 1] + chars[char]] + chars[char + 1:]
        #print('characters:')
        #print(chars)
        if chars == []:
            item =('[ :: ' + rule[2] +']', rule[0], rule[2])
        elif chars[0] not in N and chars[-1] not in N: # if word
            #print('no NTs')
            item =('[' + ''.join(chars) + ' :: ' + rule[2] +']', rule[0], rule[2])
        elif chars[0] in R: # if Rword
            #print('left restricted')
            item = ('[' + ''.join(chars[1:]) + ' :: ' + '=' + target_category[chars[0]] + ', +' + chars[0] + ', ' + rule[2] +']', rule[0], rule[2])
        elif (chars[0] not in N or len(chars) == 1) and chars[-1] in F: # if wordF
            #print('right free')
            item =('[' + ''.join(chars[:-1]) + ' :: ' + '=' + target_category[chars[-1]] + ', ' + rule[2] +']', rule[0], rule[2])
        elif chars[0] in F and chars[-1] in F: # if FwordF
            #print('2-handed free')
            item =('[' + ''.join(chars[1:-1]) + ' :: ' + '=' + target_category[chars[-1]] + ', ' + '=' + target_category[chars[0]] + ', ' + rule[2] +']', rule[0], rule[2])
        #print('item:')
        #print(item)
        MG_without_licensors += [item]
        
    #remove items whose category has no selector in the lexicon
    useless_items = []
    for item in MG_without_licensors:
        if item[2] == 'cFin':
            useless = False
        else:
            useless = True
            for other_item in MG_without_licensors:
                if '='+item[2] in other_item[0] and other_item not in useless_items:
                    useless = False
                    break
        if useless:
            useless_items += [item]
    for item in useless_items:
        MG_without_licensors.remove(item)
    
    MG = []
    for item in MG_without_licensors:
        licensors = ['-'+NT for NT in item[1] if NT in R]
        #print('licensors of ' + item[0] + ':')
        #print(licensors)
        new_item = (item[0][:-1] + ''.join([', ' + licensor for licensor in licensors]) + ']', licensors, item[2])
        MG += [new_item]
    
    all_licensors = set()
    all_licensor_chains = set()
    
    for item in MG:
        for licensor in range(len(item[1])):
            all_licensors.add((item[1][licensor],item[2]))
            if licensor < len(item[1]) - 1:
                all_licensor_chains.add((tuple(item[1][licensor:]),item[2]))
    
    for licensor in all_licensors:
        remove_shaper = ['[ :: =' + licensor[1] + ', +' + licensor[0][1:] + ', ' + licensor[1] + ']']
        #print(remove_shaper)
        MG += [remove_shaper]
        
    for chain in all_licensor_chains:
        #print('chain:')
        #print(chain)
        select_shaper = ['[ :: =' + chain[1] + ''.join([', +' + licensor[1:] for licensor in chain[0]]) + ', ' + chain[1] + ', ' +chain[0][0] + ']']
        #print(select_shaper)
        MG += [select_shaper]
        
    print('MG:')
    print('\n'.join([item[0] for item in MG]))

def vari(string):
    return string + "*"
def contr(string):
    return string + '+'

def decompose_rule(rule,R,F,N,target_category):
    '''
    Input: one rule
    Output: list of rules that the rule is decomposed into
    Assumptions: 
        N = list of all non-terminals
        F = list of all free non-terminals
        R = list of all restricted non-terminals
        vari(char) is a function that produces a uniquely indexed version of char
    '''
    symbol = rule[0]
    string = rule[1]
    if type(string) == str:
        string = list(string)
        for char in reversed(range(len(string))):
            if string[char][0] == '*' or string[char][0].isnumeric():
                string = string[:char - 1] + [string[char - 1] + string[char]] + string[char + 1:]
    categ = rule[2]
    #print('decompose ' + str(string))
    for spot in range(1, len(string) - 1):
        char = string[spot]
        if char in N:
            aux_NT = vari(char)
            aux_cat = vari(categ)
            while aux_NT in N:
                aux_NT = vari(aux_NT)
            while aux_cat in target_category.values():
                aux_cat = vari(aux_cat)
            #print('decompose into:')
            #print(string[:spot]+[aux_NT])
            #print(string[spot:])
            N.add(aux_NT)
            F += [aux_NT]
            target_category[aux_NT] = aux_cat
            return decompose_rule([symbol,string[:spot]+[aux_NT],categ],R,F,N,target_category) + decompose_rule([aux_NT,string[spot:],aux_cat],R,F,N,target_category)
    if len(string) > 1 and string[0] in R and string[-1] in R:
        #print('2-handed restricted')
        F += [contr(string[0])]
        N.add(contr(string[0]))
        target_category[contr(string[0])] = categ + string[0]
        F += [contr(string[-1])]
        N.add(contr(string[-1]))
        target_category[contr(string[-1])] = categ + string[-1]
        return [[symbol,contr(string[0])+''.join(string[1:-1])+contr(string[-1]),categ],[contr(string[0]),string[0],categ + string[0]],[contr(string[-1]),string[-1],categ + string[-1]]]
    elif len(string) > 1 and string[-1] in R:
        #print('right restricted')
        F += [contr(string[-1])]
        N.add(contr(string[-1]))
        target_category[contr(string[-1])] = categ + string[-1]
        return [[symbol,''.join(string[:-1])+contr(string[-1]),categ],[contr(string[-1]),string[-1],categ + string[-1]]]
    elif len(string) > 1 and string[0] in R and string[-1] in F:
        #print('right free, left restricted')
        F += [contr(string[0])]
        N.add(contr(string[0]))
        target_category[contr(string[0])] = categ + string[0]
        return [[symbol,contr(string[0])+''.join(string[1:]),categ],[contr(string[0]),string[0],categ + string[0]]]
    elif len(string) > 1 and string[0] in F and string[-1] not in N:
        #print('left free only')
        F += ['O']
        N.add('O')
        target_category['O'] = 'cnix'
        return [[symbol,''.join(string)+'O',categ],['O','','cnix']]
    else:
        #print('No more decomposing needed')
        return [[rule[0],''.join(rule[1]),rule[2]]]
    
def free(NT,CFG):
    NT_rules = [NT_rule for NT_rule in CFG if NT_rule[0] == NT]
    for rule in CFG:
        # check that rule is not of NT but shares a common category with NT
        if rule not in NT_rules and rule[2] in [NT_rule[2] for NT_rule in NT_rules]:
            NT_rules_of_same_category = [NT_rule for NT_rule in NT_rules if NT_rule[2] == rule[2]]
            # check if in the category rule produces a word that NT does not
            if rule[1] not in [NT_rule[1] for NT_rule in NT_rules_of_same_category]:
                #print(NT+' is not free because of '+str(rule))
                # then NT would be restricted
                return False
    return True
    '''for NT_rule in CFG:
        if NT_rule[0] == NT:
            for rule in CFG:
                if rule[0] != NT and rule[1] != NT_rule[1] and rule[2] == NT_rule[2]:
                    return False
    return True'''

def restricted(NT,CFG):
    return not free(NT,CFG)
     
        
def unify_target_category(NT,CFG,target_category,category_order):
    copy_CFG = CFG[:]
    NT_rules = [rule for rule in copy_CFG if rule[0] == NT]
    targetted_categories = [rule[2] for rule in NT_rules]
    if len(targetted_categories) > 1:
        main_category = category_order.maximum(targetted_categories)
        print('main target category of '+NT+' is '+main_category)
        target_category[NT] = main_category
        updated_NT_rules = [rule for rule in NT_rules if rule[2] == main_category]
        secondary_categories = list(set(targetted_categories) - set([main_category])) 
        print('secondary categries:')
        print(secondary_categories)
        for ind in range(len(secondary_categories)):
            updated_NT_rules += [(NT, NT+str(ind), main_category)]
            for rule in NT_rules:
                if rule[2] == secondary_categories[ind]:
                    updated_NT_rules += [(NT+str(ind), rule[1], secondary_categories[ind])]
        print('New rules:')
        print(updated_NT_rules)
        copy_CFG = [rule for rule in copy_CFG if rule not in NT_rules] + updated_NT_rules
    else:
        target_category[NT] = targetted_categories[0]
    CFG = copy_CFG[:]
    
    
def determine_partial_category_order(CFG):
    N = set([rule[0] for rule in CFG])
    category_order = partial_order([])
    for rule in CFG:
        for char in rule[1]:
            if char in N:
                for rulec in CFG:
                    if rulec[0] == char:
                        category_order.relations.add((rule[2],rulec[2]))
    return category_order

class partial_order:
    def __init__(self, relations):
        self.relations = set(relations)

    def compare(self, a, b):
        if (a, b) in self.relations:
            return True
        for r in self.relations:
            if r[0] == a and self.compare(r[1], b):
                return True
        return False
    
    def add_rule(rule):
        self.relations.add(rule)

    def maximum(self, lst):
        max_element = None
        for element in lst:
            if not max_element or self.compare(element, max_element):
                max_element = element
        return max_element

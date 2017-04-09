from parse_csv import load_csv
import numpy as np
from fractions import Fraction
import operator
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import constants.metrics

upenn_tagset = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

def count_recipe_verbs(recipe_steps):
    verbs = {}
    for step in recipe_steps:
        instruction = ' '.join(step[1:])
        words = nltk.pos_tag(nltk.word_tokenize(instruction))
        for (word, pos) in words:
            if pos in upenn_tagset:
                verb = WordNetLemmatizer().lemmatize(word,'v')
                if verb in verbs:
                    verbs[ verb ] = verbs[ verb ] + 1
                else:
                    verbs[ verb ] = 1
    return verbs

# Get k most used verbs with minimum length l
def get_k_verbs(verbs, k, l):
    sorted_verbs = sorted(verbs.iteritems(), key=operator.itemgetter(1), reverse=True)
    max_verbs = np.array([])
    for (verb, freq) in sorted_verbs:
        if len(verb) >= l:
            max_verbs = np.append(max_verbs, verb)
            if len(max_verbs) == k:
                break
    return max_verbs

def is_number(s):
    try:
        Fraction(s)
        return True
    except ValueError:
        return False

def is_metric(s):
    if s in constants.metrics.metrics:
        return True
    else:
        return False
    
def add_to_features(features, add_on):
    if features.size != 0:
        return np.concatenate((features, add_on), axis=0)  
    else:
        return add_on         

def lexical_diversity(words):
    return float( len(set(words)) ) / len(words)
        
def main():
    ##########################################################################
    recipe_steps = load_csv('./data/cheesecake/steps.csv') 

    # Preprocessing: get verb count 
    verbs = count_recipe_verbs(recipe_steps)
    
    # Get the 5 most used verbs 
    minimum_verb_len = 5 # minimum length of verb required to be accounted for 
    top_k = 10 # top k verbs 
    
    top_k_verb = get_k_verbs(verbs=verbs, k=top_k, l=minimum_verb_len)
    ###########################################################################
    # Get most used ingredients
    ingredient_counts = {}
    recipe_ingredients = load_csv("./data/cheesecake/ingredients.csv")
    stemmer = nltk.PorterStemmer()
    for ingredients in recipe_ingredients:
        ingred_id = ingredients[0]
        ingredients = ingredients[1:]
        for ingredient in ingredients:
            if ingredient == 'Add all ingredients to list': # Special case: non-ingredients are within scraped data
                continue
            ingredient = ingredient.split(',')[0]
            ingredient = ingredient.translate(None, '()')
            tokens = nltk.word_tokenize(ingredient)
            i = 0
            for token in tokens:
                token = stemmer.stem(token)
                if is_number(token):
                    i = i + 1
                    continue
                if is_metric(token):
                    i = i + 1
                    continue
                break 
            ingredient = ' '.join(tokens[i:])
            if ingredient in ingredient_counts:
                ingredient_counts[ ingredient ] = ingredient_counts[ ingredient ] + 1
            else:
                ingredient_counts[ ingredient ] = 1
    
    top_k = 10 # top max_verbs_len verbs
    top_k_ingred = sorted(ingredient_counts.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]
    top_k_ingred = [k[0] for k in top_k_ingred]

    ############################################################################
    recipe_ingredients = load_csv("./data/cheesecake/ingredients.csv")
    recipe_steps = load_csv('./data/cheesecake/steps.csv')
    basic_infos = load_csv('./data/cheesecake/basic_info.csv')
    basic_infos = np.array(basic_infos)
#    top_k_ingred = ['white sugar', 'cream cheese', 'vanilla extract', 'eggs', 'butter']
#    top_k_verb = [u'blend', u'serve', u'remain', u'combine', u'Remove', u'remove',
#                  u'refrigerate', u'chill', u'allow', u'Place']
    features = np.array([[]])
    # Ingredients
    # Length of ingredients
    ids = np.array([])
    lengths = np.array([])
    for ingredients in recipe_ingredients:
        ids = np.append(ids, ingredients[0])
        lengths = np.append(lengths, len(ingredients[1:]))
    ids.shape = (1, len(ids))
    lengths.shape = (1, len(lengths))
    features = add_to_features(features, ids)
    features = add_to_features(features, lengths)    
    
    # Existance of top k ingredients in ingredients  
    temp = np.array([[]])
    for ingredients in recipe_ingredients:
        k_ingred_feature = np.array([]) # feature array for each recipe, Ex. [1,0,1,0,1]
        ingredients = ingredients[1:] 
        for k_ingred in top_k_ingred:
            exist_k_ingred = 0
            for ingredient in ingredients:
                if ingredient.count(k_ingred):
                    exist_k_ingred = 1
                    break
            k_ingred_feature = np.append(k_ingred_feature, exist_k_ingred)
        k_ingred_feature.shape = (1, len(k_ingred_feature))
        temp = add_to_features(temp, k_ingred_feature)
    features = add_to_features(features, temp.T)
    
    # Recipe
    # Length of recipe
    lengths = np.array([])
    for steps in recipe_steps:
        lengths = np.append(lengths, len(steps[1:]))
    lengths.shape = (1, len(lengths))
    features = add_to_features(features, lengths)
    
    # Lexical richness/diversity
    lex_div = np.array([])
    for steps in recipe_steps:
        lex_div = np.append(lex_div, lexical_diversity(nltk.word_tokenize(' '.join(steps[1:]))))
    lex_div.shape = (1, len(lex_div))
    features = add_to_features(features, lex_div)
    
    # Existance of top k verbs in recipe steps
    temp = np.array([[]])
    for steps in recipe_steps:
        k_verb_feature = np.array([]) # feature array for each recipe, Ex. [1,0,1,0,1]
        steps = steps[1:] 
        for k_verb in top_k_verb:
            exist_k_verb = 0
            for step in steps:
                if step.count(k_verb):
                    exist_k_verb = 1
                    break
            k_verb_feature = np.append(k_verb_feature, exist_k_verb)
        k_verb_feature.shape = (1, len(k_verb_feature))
        temp = add_to_features(temp, k_verb_feature)
    features = add_to_features(features, temp.T)
    
    
    # Basic Info 
    # Calorie 
    calories = basic_infos[:, 5]
    calories.shape = (1, len(calories))
    features = add_to_features(features, calories)
    
    # total_time
    total_times = basic_infos[:, -1]
    for (i, time) in enumerate(total_times):
        if time == 'NA':
            continue
        day = 0
        hour = 0
        minute = 0
        remainder_string = time
#        if 'Day' in time:
#            (day, remainder_string) = time.split('Day')
#            (hour, remainder_string) = remainder_string.split('H')
#            minute = remainder_string.split('M')[0]
#        else:
#            (hour, remainder_string) = time.split('H')
#            minute = remainder_string.split('M')[0]
        if 'Day' in time:
            (day, remainder_string) = time.split('Day')
        if 'H' in time:
            (hour, remainder_string) = remainder_string.split('H')
        if 'M' in time:
            minute = remainder_string.split('M')[0]

        if not day:
            day = 0
        if not hour:
            hour = 0 
        if not minute:
            minute = 0
        time_in_minutes = float(day) * 1440 + float(hour) * 60 + float(minute)
        total_times[i] = time_in_minutes
    total_times.shape = (1, len(total_times))
    features = add_to_features(features, total_times)
    
    # Target: star_rating
    star_rating = basic_infos[:, 2]
    star_rating.shape = (1, len(star_rating))
    features = add_to_features(features, star_rating)
    
    print features.T.shape
    print features.T

if __name__ == '__main__':
    main()
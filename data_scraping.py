from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import numpy as np
import time
import csv


# ********** Methods **************
# collect all recipes urls
def collect_recipes_urls():
    #url = "http://allrecipes.com/recipes/840/desserts/cookies/chocolate-cookies/?page="
    url = "http://allrecipes.com/recipes/1537/bread/yeast-bread/bagels/?page="
    # url = "http://allrecipes.com/recipes/362/desserts/cookies/?page="
    # url = "http://allrecipes.com/recipes/810/desserts/pies/custard-and-cream-pies/lemon-pie/?page="
    page_cnt = 1
    end_of_page = False
    urls_lists = []
    while not end_of_page:

        # Get the page
        driver.get(url + str(page_cnt))

        # Check not end of the page
        try:
            driver.find_element_by_class_name("error-page__404")
            print "End of the page reached with page number: ", page_cnt
            end_of_page = True
            continue
        except:
            print "Page ", page_cnt, " still has results"

        # get all the "favorite" element
        html_list = driver.find_element_by_id("grid")
        urls = html_list.find_elements_by_class_name("favorite")

        # get the recipe id in each "favorite"
        id = []
        for i, e in enumerate(urls):
            id.append(e.get_attribute('data-id'))
            urls_lists.append('https://allrecipes.com/recipe/' + str(id[i]))
        page_cnt += 1

    print "Total number of urls without unique(): ", len(urls_lists)
    print urls_lists
    urls_lists = np.unique(urls_lists)
    total_unique_urls = len(urls_lists)
    print "Total unique urls: ", total_unique_urls
    # print urls_lists

    urls_lists = np.array(urls_lists)
    urls_lists = urls_lists.reshape((total_unique_urls, 1))
    print urls_lists

    np.savetxt("urls.csv", urls_lists, delimiter=",", fmt="%s")


# load urls
def load_urls():
    with open('urls.csv', 'rb') as f:
        reader = csv.reader(f)
        urls_list = list(reader)
        your_list_size = len(urls_list)
    urls_list = np.array(urls_list)
    urls_list = urls_list.reshape((your_list_size,))
    return urls_list


# save list of lists to csv
def to_csv(filename, data):
    with open(filename, "ab") as f:
        writer = csv.writer(f)
        writer.writerows(data)


# load data from csv
def load_csv(filename):
    total_store = []
    row_store = []
    with open(filename, 'rU') as f:  # opens PW file
        reader = csv.reader(f)
        # Print every value of every row.
        for row in reader:
            for value in row:
                row_store.append(str(value))
            total_store.append(row_store)
            row_store = []
    return total_store


# collect infos on the recipe
def scrape_recipe(br, url):

    driver.get(url)

    driver.find_element_by_class_name("icon--adjust-servings").click()
    driver.find_element_by_id("servings").clear()
    driver.find_element_by_id("servings").send_keys(1)
    radio_btn = driver.find_elements_by_class_name("radio-lbl")
    radio_btn[1].click()
    driver.find_element_by_id("btn-adjust").click()

    all_info = [] #1-basic info, 2-ingredient, 3-steps
    recipe_basic_info = []
    recipe_ingredients = []
    recipe_steps = []

    # recipe title
    try:
        title = br.find_element_by_tag_name('h1').text.encode('ascii', 'ignore')
    except:
        title = 'NA'

    # recipe id
    try:
        recipe_id = br.find_element_by_class_name('favorite').get_attribute('data-id')
    except:
        recipe_id = 'NA'

    # Star rating
    try:
        star_rating = br.find_element_by_class_name('rating-stars'). \
            get_attribute('data-ratingstars')
    except:
        star_rating = 'NA'

    # Number of people who clicked that they "made it"
    try:
        made_it_count = br.find_element_by_class_name('made-it-count').text
    except:
        made_it_count = 'NA'

    # Number of reviews
    try:
        review_count = br.find_element_by_class_name('review-count').text
        # NLCB
        review_count = str(re.findall('(\w+) reviews', review_count)[0])
    except:
        review_count = 'NA'

    # calories per serving
    try:
        cal_count = br.find_element_by_class_name('calorie-count').text
        # BUG next line
        # calcount = str(re.findall('(\w+) cals', calcount)[0])
    except:
        cal_count = 'NA'

    # prep time
    try:
        prep_time = br.find_element_by_xpath('//time[@itemprop = "prepTime"]'). \
            get_attribute('datetime')
        prep_time = str(re.findall('PT(\w+)', prep_time)[0])
    except:
        prep_time = 'NA'

    # Cook time
    try:
        cook_time = br.find_element_by_xpath('//time[@itemprop = "cookTime"]'). \
            get_attribute('datetime')
        cook_time = str(re.findall('PT(\w+)', cook_time)[0])
    except:
        cook_time = 'NA'

    # total time
    try:
        total_time = br.find_element_by_xpath('//time[@itemprop = "totalTime"]'). \
            get_attribute('datetime')
        total_time = str(re.findall('PT(\w+)', total_time)[0])
    except:
        total_time = 'NA'

    print "-----Current recipe id: ", recipe_id

    try:
        unicode(title, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        title = unicode(title, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(recipe_id, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        recipe_id = unicode(recipe_id, "utf-8")
        print "WTF"
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(star_rating, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        star_rating = unicode(star_rating, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(made_it_count, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        made_it_count = unicode(made_it_count, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(review_count, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        review_count = unicode(review_count, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(cal_count, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        cal_count = unicode(cal_count, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(prep_time, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        prep_time = unicode(prep_time, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(cook_time, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        cook_time = unicode(cook_time, "utf-8")
    else:
        # value was valid ASCII data
        pass

    try:
        unicode(total_time, "ascii")
    except TypeError:
        pass
    except UnicodeError:
        total_time = unicode(total_time, "utf-8")
    else:
        # value was valid ASCII data
        pass




    recipe_basic_info.append(recipe_id)
    recipe_ingredients.append(recipe_id)
    recipe_steps.append(recipe_id)

    recipe_basic_info.append(title)
    recipe_basic_info.append(star_rating)
    recipe_basic_info.append(made_it_count)
    recipe_basic_info.append(review_count)
    recipe_basic_info.append(cal_count)
    recipe_basic_info.append(prep_time)
    recipe_basic_info.append(cook_time)
    recipe_basic_info.append(total_time)


    # find all the ingredient attributes
    ingredients = br.find_elements_by_class_name("checkList__item")

    # Go through all ingredients and collect text
    ingredients_list = []
    for x in np.arange(len(ingredients) - 1):
        ingredients_list.append(str(ingredients[x].text.encode('ascii', 'ignore')))

    # Go through all steps
    steps = br.find_elements_by_class_name("step")
    step_list = []
    for x in np.arange(len(steps) - 1):
        step_list.append(str(steps[x].text.encode('ascii', 'ignore')))

    # update mongoDB with ingredients entry
    for ingr in ingredients_list:
        temp = {'idnumber': recipe_id,'ingredient': ingr.encode('ascii', 'ignore')}
        if not temp['ingredient'] == '':
            recipe_ingredients.append(temp['ingredient'])
            #print temp


    # update mongoDB with step entry
    for stp in step_list:
        temp = {'idnumber': recipe_id, 'step': stp.encode('ascii', 'ignore')}
        if not temp['step'] == '':
            recipe_steps.append(temp['step'])
            #print temp

    all_info.append(recipe_basic_info)
    all_info.append(recipe_ingredients)
    all_info.append(recipe_steps)

    # Update mongoDB with recipe entry
    temp = {'idnumber': recipe_id,
            'recipe_title': title.encode('ascii', 'ignore'),
            'star_rating': star_rating,
            'made_it_count': made_it_count,
            'review_count': review_count,
            'cal_count': cal_count,
            'prep_time': prep_time,
            'cook_time': cook_time,
            'total_time': total_time}
    #print temp

    return all_info


# ********* Methods ends ***********
chop = webdriver.ChromeOptions()
chop.add_extension('AdBlock_v3.9.1.crx')
driver = webdriver.Chrome(chrome_options=chop)
#collect_recipes_urls()

urls = load_urls()

all_recipes_basic_info = []
all_recipes_ingredients = []
all_recipes_steps = []

for i in range(0, len(urls)):
    print "scraping recipe ", i
    results = scrape_recipe(driver, urls[i])
    all_recipes_basic_info.append(results[0])
    all_recipes_ingredients.append(results[1])
    all_recipes_steps.append(results[2])
    if len(all_recipes_basic_info)%10 == 0:
        print "saving************"
        to_csv("basic_info.csv", all_recipes_basic_info)
        to_csv("ingredients.csv", all_recipes_ingredients)
        to_csv("steps.csv", all_recipes_steps)
        all_recipes_basic_info = []
        all_recipes_ingredients = []
        all_recipes_steps = []
    if i == len(urls)-1 and len(all_recipes_basic_info)>1:
        print "saving the left over************"
        to_csv("basic_info.csv", all_recipes_basic_info)
        to_csv("ingredients.csv", all_recipes_ingredients)
        to_csv("steps.csv", all_recipes_steps)


"""
load_csv_basic_info = load_csv("basic_info.csv")
load_csv_ingredients = load_csv("ingredients.csv")
load_csv_steps = load_csv("steps.csv")

print load_csv_basic_info[1][1]
print load_csv_ingredients[1][1]
print load_csv_steps[1][1]
"""
#driver.close()



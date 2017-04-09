************basic_info************
1. recipe_id
2. title
3. star_rating
4. made_it_count
5. review_count
6. calorie_count
7. prep_time, in XHXM format i.e. x hours x mins
8. cook_time, see 7
9. total_time, which is equal to prep+cook. see 7

***********ingredients************
1. recipe_id
2~X. its ingredients
***All the ingredients have been adjusted to just single serve and in metric units instead of american units

**************steps***************
1. recipe_id
2~X. its steps

***************url****************
if you want to look for a specific recipe, copy its id and then go to urls.csv to find its url.
number of urls = number of recipes scraped


***parse_csv.py file could help you to transform those csv to list of lists.***
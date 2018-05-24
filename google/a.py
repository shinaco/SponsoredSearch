import sys
import __init__ as g

num_page = 3
query = "This is my query";
search_results = g.search(query, num = num_page,stop=5)
for result in search_results:
    print(result)

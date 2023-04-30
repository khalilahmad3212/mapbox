import random,requests
import json
import openai
import os
import webbrowser
import json
from logo_dict import logo_map

# Set up your OpenAI API key and model name
openai.api_key = "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"
model_name = 'text-davinci-003'


# function to extract city from news article using ChatGPT
def extract_city_from_news_article(article):
    prompt = f"Extract the city, town, village, or any location information from the following news article:\n\nHeadline: {article['description']} if location is not available then give most close based on guess. If there is mo location the return N/A"
    response = openai.Completion.create(
        model=model_name,
        prompt=prompt,
        max_tokens=256,
        n=1,
        stop=None,
        temperature=0.5
    )
    city = response.choices[0].text.strip()
    return city


# dictionary to map logo and domain  

locs=set()


article_array=[]
NA_articles_array=[]

# google maps API Key
g_key="AIzaSyA_xpbVEp9woLniuF8Cl-2TG80wkte6JiU"


###    Fetching Articles and their cities


# New API key
url="https://api.goperigon.com/v1/all?apiKey=bcf9d941-c4d9-45c0-a3cf-c7658e7c63ae&from=2023-01-26&sourceGroup=top100&showNumResults=true&excludeLabel=Opinion&excludeLabel=Paid News&excludeLabel=Roundup&excludeLabel=Press Release&sortBy=date&size=50"

# Send GET request to fetch JSON data
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    # Parse JSON
    json_data = json.loads(response.text)

    # Extract "articles" attribute
    articles = json_data.get("articles", [])


   # Loop through articles and print title and description
    for article in articles:
        # Call the function with the example news article
        city = extract_city_from_news_article(article)

        article_title = article.get("title", "")
        article_url = article.get("url", "")
        article_source = article.get("source", "")
        print("\n\nArticle Title:", article_title)
        print("\nArticle URL:", article["url"])
        print("\nExtracted city:", city)
        print("\nSource:", article_source["domain"])
        
        if city.find('N/A') != -1:
            NA_articles_array.append({
                "title": article_title, 
                "url": article_url,
                "city": city,
                "domain": article_source["domain"]
            })

        else:  
            article_array.append({
                "title": article_title, 
                "url": article_url,
                "city": city,
                "domain": article_source["domain"]
            })
else:
    print("Failed to fetch JSON data. Status code:", response.status_code)



###     Fetching coordinates 

for i, article in enumerate(article_array):
    n,t,u=article["domain"], article["title"], article["url"]
    
    location = article['city']
    url=("https://maps.googleapis.com/maps/api/geocode/json?address="+location+"&key="+g_key)
    # Make HTTP GET request and parse response as JSON
    response = requests.get(url)
    data = response.json()

    # Check if "results" key is present and contains at least one element
    if "results" in data and len(data["results"]) > 0:
        # Access the first element in the "results" list
        r = data["results"][0]
        # Do whatever you want with the data in r
        r=requests.get(url).json()["results"][0]
        loc=r["geometry"]["location"]
        print(loc)
        l=(loc["lat"],loc["lng"])
        article["coordinates"] = [loc["lat"],loc["lng"]]
        if l not in locs:
            print(l)
            locs.add(l)
        else:
            while l in locs:
                _lat=(random.randint(0,1000)-500)/1000
                l=(l[0]+_lat,l[1])
            locs.add(l)
    else:
        print("No results found.")
    
    if article["domain"] in logo_map:  
        article["logo"]= "logos/"+logo_map[article["domain"]]+".png"
    else:
        article["logo"]= "logos/0.png"   

    del article['city']
    del article['domain']

    print(article)


# Convert data to JSON format
json_na_data = json.dumps(NA_articles_array)
json_data = json.dumps(article_array)

# Write JSON data to a file
with open('articles.json', 'w') as f:
    f.write(json_data)

with open('articles_na.json', 'w') as f:
    f.write(json_na_data)

# Check if the HTML file exists before opening it in a web browser
html_filename = "sample.html"
html_file_path = os.path.abspath(html_filename)
if os.path.exists(html_file_path):
    webbrowser.open("http://127.0.0.1:5500/"+html_filename)
else:
    print("HTML file does not exist.")
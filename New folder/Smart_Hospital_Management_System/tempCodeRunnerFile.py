import requests
API_KEY='a67ff8af513644a890cf681916c3484c'
endpoint = 'https://newsapi.org/v2/top-headlines'
news_parameters ={
    'sources': 'google-news-in',
    'apiKey': API_KEY,
    #'pageSize': 10,
    #'category': 'health',

}
response_s = requests.get(endpoint,params=news_parameters)
print(response_s.status_code)
d=response_s.json()
print()
import requests
import time
import json
from tqdm import tqdm


def query_paper(paperName, max_retries=3):
    url = f'https://api.semanticscholar.org/graph/v1/paper/search/match?query={paperName}'
    query_params = {"fields": "title,year,authors,citationCount,influentialCitationCount,url"}
    
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=query_params)
        except ConnectionResetError:
            print("Connection reset by peer. Waiting before retrying...")
            time.sleep(2 ** retries)
            continue
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Request limit reached. Waiting before retrying...")
            time.sleep(2 ** retries) # Exponential backoff
            retries += 1
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
            return None
        
        time.sleep(1)
    
    print("Max retries reached. Request failed.")
    return None

if __name__ == '__main__':
    for i in range(4, 24):
        print(f'check sigir 20{i:02}')
        papers = json.load(open(f'json/sigir{i:02}.json'))
        
        paper_with_citations = []
        for paper in tqdm(papers):
            title = paper['title'].replace(' \n\n', '')
            res = query_paper(title)
            if res:
                paper.update({**res['data'][0], 'authors': ', '.join([i['name'] for i in res['data'][0]['authors']])})
                paper_with_citations.append(paper)
        json.dump(paper_with_citations, open(f'sigir{i:02}_with_citations.json', 'w+', encoding='utf-8'), indent=4)
        # json.dump(paper_with_citations, open(f'sigir_papers_with_citations.json', 'w+', encoding='utf-8'), indent=4)
        
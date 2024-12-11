import re
from pdfminer.high_level import extract_text
import openai
import json
from tqdm import tqdm

def parse_papers_with_gpt(text):
    """
    Parse the complex papers information using GPT-4 model
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant for a research conference."},
        {"role": "user", "content": f"Parse the following text into a list of dictionaries containing the paper title, list of authors, and list of affiliations. Return the result in JSON format. For duplicate affiliations, mention them only once in the affiliations list:\n\n{text}\n\nOutput format:\n[{{'title': 'Paper title', 'authors': ['author1', 'author2'], 'affiliations': ['affiliation1', 'affiliation2']}}]"}
    ]

    try:   
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.5,
        )
        text = json.loads(response.choices[0].message.content)
    except Exception as e:
        print(e)
    return text

def parse_papers(text):
    """
    Parse the papers information using regular expression in most cases
    """
    paper = re.split(r'\.* ?(?:\d+|[0-9]) ?\n', text)
    title = paper[0].strip().replace('\n', '')
    try:
        authors_affiliations = paper[1].strip()
    except IndexError:
        print('IndexError:', text)
        return {
            'title': title,
            'authors': [],
            'affiliations': []
        }
    
    authors = re.findall(r'([A-Za-zÀ-ÖØ-öø-ÿ\s,.]+)\s*\(([^)]+)\)', authors_affiliations)
    
    authors_list = []
    affiliations_set = set()
    
    for author, affiliation in authors:
        if ', ' in author:
            author = [a.strip() for a in author.split(', ') if len(a.strip()) > 0]
            authors_list.extend(author)
        else:
            authors_list.append(author.strip())
        affiliations_set.add(affiliation.strip())
    
    return {
        'title': title,
        'authors': authors_list,
        'affiliations': list(affiliations_set)
    }

def parse_pdf(file_path):
    text = extract_text(file_path)
    toc = text.split('Table of Contents')[1]
    marker = '•' if '•' in toc else '\uf0b7'
    print(toc.count(marker))
    
    pattern = re.compile(r'\.* ?(?:\d+|[0-9]) ?\n') # Title ... 1234 \n Author1 (Affiliation1), Author2(Affiliation2)

    papers = []
    for paper_block in tqdm(toc.split(marker)[1:]):
        valid_paper = paper_block.strip()
        if len(valid_paper) > 0 and '(' in valid_paper:
            matches = pattern.findall(valid_paper)
            if len(matches) > 2:
                print(len(matches), matches)
                print('call gpt for :', valid_paper)
                res = parse_papers_with_gpt(valid_paper)
                if isinstance(res, list):
                    papers.extend(res)
                else:
                    papers.append(parse_papers(text))
            else:
                papers.append(parse_papers(valid_paper))
                
    return papers


if __name__ == '__main__':
    openai.api_key = 'your-openai-api-key'
    openai.base_url = "your-openai-base-url"
    
    for i in range(4, 24):
        print(f'Parsing PDF {i:02}.pdf')
        papers = parse_pdf(f'../sigir/pdf/{i:02}.pdf')
        json.dump(papers, open(f'../sigir/json/sigir{i:02}.json', 'w+', encoding='utf-8'), indent=4)
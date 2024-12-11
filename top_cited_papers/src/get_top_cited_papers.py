import json
import pandas as pd

def gen_markdown(top:pd.DataFrame):
    md = pd.DataFrame()
    md['title'] = top['title'].apply(lambda x: f'[{x}]({top[top["title"]==x]["url"].values[0]})')
    if isinstance(top['authors'], list):
        authors = top['authors'].apply(lambda x: ', '.join([i['name'] for i in x]))
    else:
        authors = top['authors']
    md['authors'] = authors
    md['affiliations'] = top['affiliations'].apply(lambda x: ', '.join(x))
    md['citationCount'] = top['citationCount']
    md['influentialCitationCount'] = top['influentialCitationCount']
    md['year'] = top['year']
    # print(md)
    return md.to_markdown(index=False)

def gen_docs(papers, year, file_path='../sigir/sigir_top_cited_papers.md'):
    """
    Generate markdown paper list for top cited papers of a year
    """
    top = pd.DataFrame(papers)
    with open(file_path,'a+') as f:
        f.write(f'## SIGIR {year}\n')
        f.write(gen_markdown(top))
        f.write('\n\n')
        
if __name__ == '__main__':
    for i in range(4, 24):
        print(f'check sigir 20{i:02}')
        papers = json.load(open(f'../sigir/json/sigir{i:02}_with_citations.json'))
        gen_docs(papers, f'20{i:02}', '../sigir/sigir_top_cited_papers.md')
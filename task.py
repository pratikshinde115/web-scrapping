import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
df = pd.read_excel('Input.xlsx')


#negative words
with open("MasterDictionary/positive-words.txt", "r") as file:
    positive = file.read().replace('\n', ' ')
#positive words
with open("MasterDictionary/negative-words.txt", "r", encoding='ISO-8859-1') as file:
    negative = file.read().replace('\n', ' ')

#stopwords
with open("StopWords/StopWords_Auditor.txt", "r",encoding='ISO-8859-1') as file:
    StopWords_Auditor = file.read().split('\n')
with open("StopWords/StopWords_Currencies.txt", "r" ,encoding='ISO-8859-1') as file:
    StopWords_Currencies = file.read().split('\n')

with open("StopWords/StopWords_DatesandNumbers.txt", "r" ,encoding='ISO-8859-1') as file:
    StopWords_DatesandNumbers = file.read().split('\n')
    
    
with open("StopWords/StopWords_Generic.txt", "r" ,encoding='ISO-8859-1') as file:
    StopWords_Generic = file.read().split('\n')
    
    
with open("StopWords/StopWords_GenericLong.txt", "r" ,encoding='ISO-8859-1') as file:
    StopWords_GenericLong = file.read().split('\n')
    
    
with open("StopWords/StopWords_Geographic.txt", "r" ,encoding='ISO-8859-1') as file:
    StopWords_Geographic = file.read().split('\n')
    
with open("StopWords/StopWords_Names.txt", "r" ,encoding='ISO-8859-1') as file:
    StopWords_Names = file.read().split('\n')


StopWords_DatesandNumbers = [term.split('|')[0].strip() for term in StopWords_DatesandNumbers]
StopWords_Currencies = [term.split('|')[0].strip() for term in StopWords_Currencies]
StopWords_Geographic = [term.split('|')[0].strip() for term in StopWords_Geographic]
StopWords_Names = [term.split('|')[0].strip() for term in StopWords_Names]


stopwords = StopWords_Auditor +StopWords_Currencies+StopWords_DatesandNumbers+StopWords_Generic+StopWords_GenericLong+StopWords_Geographic+StopWords_Names

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

text_analysis = {}




def count_pos_neg(cleaned_text,pos_neg):
    pos_neg_count = 0
    for i in cleaned_text.split():
        if i in pos_neg.split():
            pos_neg_count +=1
    return pos_neg_count

def get_text(url , stopwords):
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    text = soup.find("div", {"class": "td-post-content"})
    if text is not None:
        text = str(text.text)
        cleaned_text = re.sub(r'[\n\xa0]', '', text)
        pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, stopwords)))
        cleaned_text = re.sub(pattern, '', cleaned_text)
        text = re.sub(r'[?!,.]', '', cleaned_text)
        cleaned_text = cleaned_text.lower()
        return cleaned_text , text
    else:
        
        return "page not found.","0"


def save(cleaned_text,text ,count):
    file_name=df['URL_ID'][count]
    Positive_Score = count_pos_neg(cleaned_text , positive)
    Negative_Score = count_pos_neg(cleaned_text , negative)
    POLARITY_SCORE=(Positive_Score - Negative_Score)/ ((Positive_Score + Negative_Score) + 0.000001)
    Subjectivity_Score = (Positive_Score + Negative_Score)/ ((len(cleaned_text.split())) + 0.000001)
    Average_Sentence_Length = len(cleaned_text.split('.')) / len(cleaned_text.split())
    Percentage_of_Complex_words = len(text.split()) / len(cleaned_text.split()) 
    Fog_Index = 0.4 * (Average_Sentence_Length + Percentage_of_Complex_words)
    
    if 'Positive_Score' not in text_analysis:
        text_analysis['Positive_Score'] = []
    text_analysis['Positive_Score'].append(Positive_Score)
    if 'Negative_Score' not in text_analysis:
        text_analysis['Negative_Score'] = []
    text_analysis['Negative_Score'].append(Negative_Score)
    if 'POLARITY_SCORE' not in text_analysis:
        text_analysis['POLARITY_SCORE'] = []
    text_analysis['POLARITY_SCORE'].append(POLARITY_SCORE)
    if 'Subjectivity_Score' not in text_analysis:
        text_analysis['Subjectivity_Score'] = []
    text_analysis['Subjectivity_Score'].append(Subjectivity_Score)
    if 'Average_Sentence_Length' not in text_analysis:
        text_analysis['Average_Sentence_Length'] = []
    text_analysis['Average_Sentence_Length'].append(Average_Sentence_Length)
    if 'Percentage_of_Complex_words' not in text_analysis:
        text_analysis['Percentage_of_Complex_words'] = []
    text_analysis['Percentage_of_Complex_words'].append(Percentage_of_Complex_words)
    if 'Fog_Index' not in text_analysis:
        text_analysis['Fog_Index'] = []
    text_analysis['Fog_Index'].append(Fog_Index)

    file = open(f"{file_name}.txt", "w")
    file.write(cleaned_text)
    file.close()
    
    
for count,url in enumerate(df['URL']):
    print(count)
    data,text = get_text(url , stopwords)
    if text == "page not found.":
        continue
    

    save(data,text,count)
    
    


df = pd.DataFrame(text_analysis)



print(df.head())
df.to_excel('df')
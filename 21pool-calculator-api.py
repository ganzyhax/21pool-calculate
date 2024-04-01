


from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import gzip
import pandas as pd
from io import BytesIO
def bitcoinPrice():
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(key)   
    data = data.json() 
    num_int = int(float(data['price']))
    return num_int
def getDiffuculty():
    url = "https://blockchair.com/bitcoin"
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    list_items = soup.find_all('div')
    local_diff = str(list_items[176].text.strip()).split(' ')[0].replace(',','')
    return float(local_diff)

def getAvarage():
    response = requests.get('https://gz.blockchair.com/bitcoin/blocks/')
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_tags = soup.find_all('pre')
    a_tags = pre_tags[0].find_all('a')
    today_data =a_tags[-1].get('href')
    url = 'https://gz.blockchair.com/bitcoin/blocks/'+today_data
    response = requests.get(url)

    # Ensure the request was successful
    if response.status_code == 200:
        gzip_file = BytesIO(response.content)

        with gzip.open(gzip_file, 'rt') as f:
            
            df = pd.read_csv(f,sep='\t')
            # get Avarage
            df['fee_total_normalized'] = df['fee_total'] / 100000000
            sum_fee_total = df['fee_total_normalized'].sum()
            length_fee_total = len(df['fee_total'])
            average_fee_total_manual = sum_fee_total / length_fee_total if length_fee_total > 0 else 0
            formatted_result = "{:.17f}".format(average_fee_total_manual)
            # get difficultyAvarage
            df['diff_total_normalized'] = df['difficulty']
            sum_fee_total = df['diff_total_normalized'].sum()
            length_fee_total = len(df['difficulty'])
            average_fee_total_manual = sum_fee_total / length_fee_total if length_fee_total > 0 else 0
        
        return [float(formatted_result),average_fee_total_manual]
    else:
        print("Failed to retrieve the file")
app = Flask(__name__)
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    hashrate = float(data.get('hashrate'))
    fee = float(data.get('fee'))
    difficulty = getDiffuculty() # in local
    realAvarage  =getAvarage() # in local
    result = (24*60*60*(6.25 + realAvarage[0]) * hashrate * 1000000000000 / 4294967296 / realAvarage[1]) * (1 - fee/100)
    result = round(result, 13)
    res = {"res":result,"difficulty":realAvarage[1],"avarage":realAvarage[0]}
    return jsonify({'result': res})
@app.route('/btcPrice', methods=['POST'])
def price():
    btcPrice = bitcoinPrice()
    res = {"res":btcPrice}
    return jsonify({'result': res})

if __name__ == '__main__':
    app.run(debug=True)


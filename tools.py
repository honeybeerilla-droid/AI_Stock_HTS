# tools.py
import os
import requests
from bs4 import BeautifulSoup
import OpenDartReader
import yfinance as yf

def get_financial_data(ticker):
    # 주가 및 재무 정보 수집
    try:
        stock = yf.Ticker(ticker)
        return {"종목명": stock.info.get('shortName', ticker), "현재가": stock.info.get('currentPrice', 'N/A'), "PER": stock.info.get('trailingPE', 'N/A')}
    except Exception as e:
        return {"에러": str(e)}

def get_naver_research(ticker):
    # 네이버 증권 리포트 수집
    try:
        code = ticker.split('.')[0]
        url = f"https://finance.naver.com/research/company_list.naver?searchType=itemCode&searchItemCode={code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
        
        reports = []
        table = soup.find('table', class_='type_1')
        if table:
            for row in table.find_all('tr')[2:7]:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    reports.append(f"[{cols[4].text.strip()}] {cols[1].text.strip()} ({cols[2].text.strip()})")
        return reports if reports else ["최근 리포트 없음"]
    except Exception as e:
        return [f"리서치 수집 에러: {e}"]

def get_dart_disclosure(ticker, api_key):
    # DART 전자공시 수집
    if not api_key: return ["DART API Key 없음"]
    try:
        dart = OpenDartReader(api_key)
        code = ticker.split('.')[0]
        disclosures = dart.list(code)
        if disclosures is not None and not disclosures.empty:
            return [f"[{row['rcept_dt']}] {row['report_nm']}" for _, row in disclosures.head(5).iterrows()]
        return ["최근 공시 없음"]
    except Exception as e:
        return [f"공시 수집 에러: {e}"]
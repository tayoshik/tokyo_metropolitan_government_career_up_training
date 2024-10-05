import pandas as pd
from bs4 import BeautifulSoup
import random
import string
from datetime import datetime
import os
import re

print(f"プログラム開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def generate_random_string(length=8):
    """ランダムな文字列を生成する関数"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def convert_to_half_width(s):
    """全角文字（数字、スラッシュ）を半角文字に変換する関数"""
    full_width = "０１２３４５６７８９／"
    half_width = "0123456789/"
    trans_table = str.maketrans(full_width, half_width)
    return s.translate(trans_table)

def convert_to_english_date(date_str):
    """日本語の日付をmm/dd形式に変換する関数"""
    # 全角文字を半角文字に変換
    date_str = convert_to_half_width(date_str)
    
    # 年月日形式の場合
    ymd_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
    if ymd_match:
        month = ymd_match.group(2).zfill(2)
        day = ymd_match.group(3).zfill(2)
        return f"{month}/{day}"
    
    # 月日形式の場合
    md_match = re.search(r'(\d{1,2})/(\d{1,2})', date_str)
    if md_match:
        month = md_match.group(1).zfill(2)
        day = md_match.group(2).zfill(2)
        return f"{month}/{day}"
    
    # 日本語形式の場合
    jp_match = re.search(r'(\d+)月(\d+)日', date_str)
    if jp_match:
        month = jp_match.group(1).zfill(2)
        day = jp_match.group(2).zfill(2)
        return f"{month}/{day}"
    
    return ""

print("HTMLファイルを読み込みます")
try:
    with open('tokyo_metropolitan_government_career_up_training.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    print(f"HTMLファイルの長さ: {len(html_content)} 文字")
except Exception as e:
    print(f"HTMLファイルの読み込みでエラーが発生しました: {e}")
    exit(1)

print("BeautifulSoupオブジェクトを作成します")
soup = BeautifulSoup(html_content, 'html.parser')

print("講座名を抽出します")
lectures = []
for kamoku_name in soup.find_all('tr', class_='kamokuName'):
    a_tag = kamoku_name.find('a')
    if a_tag:
        lectures.append(a_tag.get_text().strip())

print(f"抽出された講座名の数: {len(lectures)}")

print("データを格納するリストを初期化します")
data_list = []

print("各講習の詳細情報を抽出します")
for kamoku_name in soup.find_all('tr', class_='kamokuName'):
    a_tag = kamoku_name.find('a')
    if a_tag:
        lecture_name = a_tag.get_text().strip()
        print(f"講座名: {lecture_name}")
        
        location_row = kamoku_name.find_next_sibling('tr', class_='kouName')
        location = location_row.find('td').text.strip() if location_row else "不明"
        print(f"実施場所: {location}")
        
        nendo_row = kamoku_name.find_next_sibling('tr', class_='nendo')
        if nendo_row:
            no = convert_to_half_width(nendo_row.find('td').text.strip().split('No.')[-1].strip())
            print(f"No.: {no}")
            
            date_row = nendo_row.find_next_sibling('tr')
            if date_row:
                date_cell = date_row.find('td', class_='table-th', string='実施日(曜日)')
                if date_cell:
                    dates = date_cell.find_next_sibling('td').text.strip().split('、')
                    print(f"実施日: {dates}")
                    
                    for date in dates:
                        english_date = convert_to_english_date(date)
                        data_list.append({
                            'No.': no,
                            '講座名': lecture_name,
                            '実施場所': location,
                            '実施日': date.strip(),
                            '実施日英語': english_date
                        })
                    print(f"{len(dates)}行のデータをリストに追加しました")
                else:
                    print("実施日のセルが見つかりません")
            else:
                print("実施日の行が見つかりません")
        else:
            print("No.の行が見つかりません")

print(f"抽出された詳細データの数: {len(data_list)}")

print("DataFrameを作成します")
df = pd.DataFrame(data_list)
print(f"DataFrameの形状: {df.shape}")
print("DataFrameの最初の数行:")
print(df.head())

print("ランダムな文字列を生成してファイル名に追加します")
random_string = generate_random_string()
output_filename = f'careerup_courses_{random_string}.csv'
print(f"出力ファイル名: {output_filename}")

print("CSVファイルとして出力します")
try:
    df.to_csv(output_filename, index=False, encoding='utf-8-sig', sep=',')
    print(f"CSVファイルの出力に成功しました")
    print(f"ファイルサイズ: {os.path.getsize(output_filename)} バイト")
except Exception as e:
    print(f"CSVファイルの出力でエラーが発生しました: {e}")

print(f"講習情報を {output_filename} に出力しました。")
print(f"プログラム終了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

import os
import time
import requests
import random
import re
from google import genai
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")

# --- 1. WordPressからランダム取得 ---
def get_random_article():
    SITE_URL = "https://info-study.com/wp-json/wp/v2/posts"
    try:
        res = requests.get(SITE_URL, params={'per_page': 1})
        total_posts = int(res.headers.get('X-WP-Total', 0))
        random_page = random.randint(1, total_posts)
        article = requests.get(SITE_URL, params={'per_page': 1, 'page': random_page}).json()[0]
        return {
            "title": article['title']['rendered'],
            "link": article['link'],
            "content": article['content']['rendered']
        }
    except Exception as e:
        print(f"❌ WP取得エラー: {e}")
        return None

# --- 2. 最新Gemini 3 Flash で要約 ---
def generate_summary(article):
    client = genai.Client(api_key=GEMINI_API_KEY)
    clean_text = re.sub('<[^<]+?>', '', article['content'])
    prompt = f"以下の学習コラムの内容をThreads向けに魅力的に要約して。150文字程度。最後に『続きはリプライのリンクからチェック！』と入れて。\n\nタイトル：{article['title']}\n内容：{clean_text[:2000]}"
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

# --- 3. Threads投稿（監視・公開プロセス） ---
def post_to_threads_with_check(text, reply_to_id=None):
    base_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    
    params = {
        'access_token': THREADS_ACCESS_TOKEN,
        'text': text,
        'media_type': 'TEXT'  # 【ここを追加】テキスト投稿であることを明示
    }
    
    if reply_to_id:
        params['reply_to_id'] = reply_to_id
        
    # A. コンテナ作成
    res = requests.post(base_url, params=params).json()
    creation_id = res.get('id')
    
    if not creation_id:
        print(f"❌ コンテナ作成失敗: {res}")
        return None

    # (以下、ステータス監視と公開プロセスは同じです)
    print(f"   投稿準備中 (ID: {creation_id})...")
    for _ in range(10):
        status_res = requests.get(
            f"https://graph.threads.net/v1.0/{creation_id}", 
            params={'fields': 'status_code', 'access_token': THREADS_ACCESS_TOKEN}
        ).json()
        
        status = status_res.get('status_code')
        if status == 'FINISHED':
            break
        elif status == 'ERROR':
            print(f"❌ Meta側エラー: {status_res}")
            return None
        time.sleep(3)

    # C. 公開（Publish）
    publish_res = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish", 
        params={'creation_id': creation_id, 'access_token': THREADS_ACCESS_TOKEN}
    ).json()
    
    return publish_res.get('id')

# --- 実行 ---
if __name__ == "__main__":
    article_data = get_random_article()
    
    if article_data:
        print(f"✅ 記事取得: {article_data['title']}")
        summary = generate_summary(article_data)
        
        print("\n1/2 親ポストを送信中...")
        parent_post_id = post_to_threads_with_check(summary)
        
        if parent_post_id:
            print("✅ 親ポスト公開成功！")
            time.sleep(2) # 念のためのバッファ
            
            print("2/2 リプライ（リンク）を送信中...")
            link_text = f"▼詳細はこちらからチェック！\n{article_data['link']}"
            reply_id = post_to_threads_with_check(link_text, reply_to_id=parent_post_id)
            
            if reply_id:
                print("\n🚀 完璧です！すべて公開されました。Threadsを確認してください。")
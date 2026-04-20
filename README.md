# Educational Bot Project

WordPress の記事をランダムで取得し、Gemini で Threads 向けに要約して、親ポストとリンク付きリプライを投稿するスクリプトです。

## セットアップ

1. Python を用意します
2. 依存パッケージをインストールします

```bash
pip install -r requirements.txt
```

3. `.env.example` を参考に `.env` を作成します

```env
GEMINI_API_KEY=your_gemini_api_key
THREADS_ACCESS_TOKEN=your_threads_access_token
THREADS_USER_ID=your_threads_user_id
GEMINI_MODELS=gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash
```

4. `.env` に実際の値を設定します

```env
GEMINI_API_KEY=あなたのGemini APIキー
THREADS_ACCESS_TOKEN=あなたのThreadsアクセストークン
THREADS_USER_ID=あなたのThreadsユーザーID
GEMINI_MODELS=gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash
```

## 環境変数

- `GEMINI_API_KEY`: Gemini API キー
- `THREADS_ACCESS_TOKEN`: Threads Graph API のアクセストークン
- `THREADS_USER_ID`: Threads のユーザーID
- `GEMINI_MODELS`: 試行したい Gemini モデルを優先順でカンマ区切り指定
- `GEMINI_MODEL`: 単一モデル指定をしたい場合のみ利用

`GEMINI_MODELS` が設定されている場合は、その順番でモデルを試します。未設定時は `GEMINI_MODEL` を使い、さらに未設定なら `gemini-2.5-flash` を使います。

## おすすめのモデル順

自動投稿用途では、次の順番がおすすめです。

1. `gemini-2.5-flash`
2. `gemini-2.5-flash-lite`
3. `gemini-2.0-flash`

理由は、要約の品質と応答速度、混雑時の切替先としての実用性のバランスが良いためです。

## 実行方法

```bash
python main.py
```

## 実行までの手順

1. `pip install -r requirements.txt` を実行します
2. `.env.example` を参考に `.env` を作成します
3. `.env` に API キーとユーザーIDを設定します
4. `GEMINI_MODELS` を次のように設定します

```env
GEMINI_MODELS=gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash
```

5. `python main.py` を実行します

## GitHub Actions 設定

GitHub Actions で自動実行する場合は、リポジトリの `Settings` から次を設定します。

### Secrets に設定するもの

- `GEMINI_API_KEY`
- `THREADS_ACCESS_TOKEN`
- `THREADS_USER_ID`

### Variables に設定するもの

- `GEMINI_MODELS`

おすすめ値:

```text
gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash
```

### 設定手順

1. GitHub の対象リポジトリを開きます
2. `Settings` -> `Secrets and variables` -> `Actions` を開きます
3. `Secrets` タブで次の3つを追加します
4. `Variables` タブで `GEMINI_MODELS` を追加します
5. `Actions` タブから `Threads Auto Post & Keepalive` を手動実行するか、定期実行を待ちます

`GEMINI_MODELS` を未設定でもローカルコード側の既定値で動作しますが、GitHub Actions でも明示的に設定しておくと運用が分かりやすくなります。

## 動作概要

1. WordPress から記事を 1 件ランダム取得
2. Gemini で Threads 向け本文を生成
3. 親ポストを投稿
4. 記事リンクをリプライとして投稿

## Gemini の再試行と自動切替

- Gemini が混雑して `503` または `UNAVAILABLE` を返した場合、同じモデルで再試行します
- 再試行上限に達した場合、次のモデルへ自動で切り替えます
- すべての候補モデルで失敗した場合は、その回の投稿を中止します

例:

```env
GEMINI_MODELS=gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash
```

この場合、まず `gemini-2.5-flash` を試し、混雑で失敗し続けた場合は `gemini-2.5-flash-lite`、さらに失敗した場合は `gemini-2.0-flash` に切り替わります。

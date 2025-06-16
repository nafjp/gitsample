# 在庫管理システム (Inventory Management System)

シンプルな在庫管理アプリケーションのプロトタイプです。Flaskで構築されており、Render.comにデプロイできます。
(This is a prototype of a simple inventory management application. It is built with Flask and can be deployed to Render.com.)

## ローカルでの実行方法 (How to Run Locally)

**Prerequisites:**
*   Python 3.x
*   pip

**Steps:**
1.  リポジトリをクローンします。(Clone the repository.)
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  (任意) Pythonの仮想環境を作成して有効化します。(Optional: Create and activate a Python virtual environment.)
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```
3.  必要なライブラリをインストールします。(Install required libraries.)
    ```bash
    pip install -r requirements.txt
    ```
4.  アプリケーションを実行します。(Run the application.)
    ```bash
    python app.py
    ```
5.  ブラウザで `http://127.0.0.1:5000` を開きます。(Open `http://127.0.0.1:5000` in your browser.)

## Renderへのデプロイ手順 (Deployment Steps for Render)

**前提条件 (Prerequisites):**
*   GitHubアカウント。(GitHub account.)
*   Renderアカウント。(Render account.)
*   このリポジトリがご自身のGitHubアカウントにフォークまたはプッシュされていること。(This repository is forked or pushed to your own GitHub account.)

**手順 (Steps):**
1.  **Renderダッシュボードにログインします。** (Log in to your Render dashboard.)
2.  **"New +" ボタンをクリックし、"Web Service" を選択します。** (Click the "New +" button and select "Web Service".)
3.  **リポジトリを接続します。** "Build and deploy from a Git repository" を選択し、ご自身のGitHubアカウントを接続して、このアプリケーションのリポジトリを選択します。(Connect your repository. Select "Build and deploy from a Git repository", connect your GitHub account, and choose this application's repository.)
4.  **サービス設定を構成します:** (Configure the service settings:)
    *   **Name:** 任意の名前に設定します (例: `inventory-app`)。(Set any name you like, e.g., `inventory-app`).
    *   **Region:** 最寄りのリージョンを選択します。(Choose the region closest to you.)
    *   **Branch:** デプロイするブランチを選択します (例: `main` または `master`)。(Select the branch to deploy, e.g., `main` or `master`).
    *   **Root Directory:** (空白のまま / Leave blank if app.py is in root, or set if it's in a subdirectory). 今回は空白のままでOKです。
    *   **Runtime:** `Python 3` を選択します。(Select `Python 3`.)
    *   **Build Command:** `pip install -r requirements.txt` (This should be auto-detected from `requirements.txt` but confirm.)
    *   **Start Command:** `gunicorn app:app --log-file=-` (This should be auto-detected from the `Procfile` but confirm.)
    *   **Instance Type:** `Free` を選択します (プロトタイプの場合)。(Select `Free` for the prototype.)
5.  **(任意) 環境変数 (Environment Variables):** (Optional)
    *   このアプリケーションでは、現時点では特別な環境変数は必要ありません。 `PORT` はRenderによって自動的に設定されます。(This application does not require special environment variables at this time. `PORT` is automatically set by Render.)
6.  **"Create Web Service" ボタンをクリックします。** (Click the "Create Web Service" button.)
7.  Renderがアプリケーションのビルドとデプロイを開始します。完了すると、アプリケーションのURL (`xxxx.onrender.com`) が提供されます。(Render will start building and deploying your application. Once completed, a URL for your application (e.g., `xxxx.onrender.com`) will be provided.)
8.  提供されたURLにアクセスして、アプリケーションを確認します。(Access the provided URL to check your application.)

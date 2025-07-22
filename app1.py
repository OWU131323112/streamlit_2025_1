import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import os

# ページ設定
st.set_page_config(page_title="推し活メモリアル", layout="wide")
st.title("推し活メモリアル")

# APIキー設定
api_key = st.secrets["GEMINI_API_KEY"]

# データ読み込み
DATA_PATH = "oshi_data.csv"
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = pd.DataFrame(columns=["日付", "推し名", "活動内容", "金額", "メモ"])
    df.to_csv(DATA_PATH, index=False)

# サイドバーメニュー
menu = st.sidebar.selectbox("📌 メニューを選んでね", [
    "推しリスト表示",
    "活動を記録",
    "推し活スケジュールAIプランナー",  # ← 変更済み
    "推し活分析ダッシュボード"
])

# 推しリスト表示
if menu == "推しリスト表示":
    st.subheader("📋 推し活ログ")
    if df.empty:
        st.info("まだ推し活の記録がありません。")
    else:
        st.dataframe(df)

# 活動を記録（追加 + 削除）
elif menu == "活動を記録":
    st.subheader("📝 新しい推し活を記録")

    with st.form("record_form"):
        date = st.date_input("日付")
        oshi = st.text_input("推しの名前")
        activity = st.text_input("活動内容（例: ライブ、配信、グッズ購入）")
        amount = st.number_input("支出金額（円）", 0)
        memo = st.text_area("感想・メモ")
        submitted = st.form_submit_button("追加する")

        if submitted:
            new_data = pd.DataFrame([[date, oshi, activity, amount, memo]],
                                    columns=["日付", "推し名", "活動内容", "金額", "メモ"])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("✅ 推し活を記録しました！")

    st.markdown("### ✂️ 記録を削除したいときはこちら")

    if not df.empty:
        df_display = df.copy()
        df_display.index.name = "行番号"
        rows_to_delete = st.multiselect("削除したい行を選んでください（行番号）", df_display.index.tolist())

        if st.button("🗑️ 選択した記録を削除"):
            if rows_to_delete:
                df = df.drop(rows_to_delete).reset_index(drop=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("🧹 記録を削除しました")
            else:
                st.warning("削除する行を選んでください")

        st.markdown("### 📋 現在の推し活一覧")
        st.dataframe(df_display)
    else:
        st.info("まだ記録がありません")

# 推し活スケジュールAIプランナー
elif menu == "推し活スケジュールAIプランナー":
    st.subheader("🗓️ 推し活スケジュールAIプランナー")

    st.markdown("以下の情報を入力すると、AIが推し活プランを提案してくれるよ！")

    oshi_name = st.text_input("推しの名前")
    birthday = st.date_input("推しの誕生日")
    anniversary = st.date_input("推しの記念日（デビュー日など）")
    upcoming_events = st.text_area("今後の予定イベント（日程や内容を自由に入力）")

    if st.button("📅 プランを提案して！"):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            full_prompt = f"""
            あなたは推し活スケジュールの専門家です。
            以下の情報をもとに、ファンが取るべき行動や準備のアイデアを時系列で提案してください。
            
            【推しの名前】{oshi_name}
            【誕生日】{birthday}
            【記念日】{anniversary}
            【今後のイベント予定】{upcoming_events}

            出力例：
            - 1週間前：グッズの予約を済ませておくと◎
            - 3日前：SNSでカウントダウン投稿しよう！
            - 当日：オンラインイベントでリアタイ参戦を！

            ユーザーが楽しく過ごせるよう、前向きでやさしい言葉で提案してください。
            """

            response = model.generate_content(full_prompt)
            st.success("📌 推し活プランの提案はこちら！")
            st.write(response.text)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# ダッシュボード
elif menu == "推し活分析ダッシュボード":
    st.subheader("📊 推し活のデータ分析")

    if df.empty:
        st.warning("記録がありません。活動を記録してください。")
    else:
        df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
        df["月"] = df["日付"].dt.to_period("M").astype(str)
        monthly_spending = df.groupby("月")["金額"].sum()

        st.markdown("### 💸 月別推し活支出")
        st.bar_chart(monthly_spending)

        st.markdown("### 🧑‍🎤 推し別活動数")
        oshi_counts = df["推し名"].value_counts()
        st.bar_chart(oshi_counts)

        st.markdown("### 💡 最近の活動")
        st.dataframe(df.sort_values("日付", ascending=False).head(10))

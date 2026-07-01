import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

from src.knowledge_map import KnowledgeMap
from src.zenn_client import ZennClient

st.set_page_config(page_title="Zenn ブログ分析", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  /* Lagoon light theme */
  :root {
    --turquoise: #2EBFB3;
    --turquoise-light: #E6F7F6;
    --sand: #FAF7F2;
    --sand-dark: #EDE8DF;
    --palm: #4A7C59;
    --sea-glass: #8ECFCC;
    --coral: #D4A574;
    --deep: #1A5F7A;
  }

  .stApp { background-color: var(--sand); }

  h1, h2, h3 { color: var(--deep); font-weight: 700; }

  .section-card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid var(--sand-dark);
    box-shadow: 0 2px 8px rgba(26,95,122,0.06);
  }

  .section-title {
    color: var(--deep);
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 2px solid var(--turquoise);
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
  }

  .habit-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--sand-dark);
  }

  .habit-rank {
    color: var(--turquoise);
    font-weight: 700;
    min-width: 2rem;
    font-size: 1rem;
  }

  .habit-phrase {
    background: var(--turquoise-light);
    color: var(--deep);
    padding: 0.2rem 0.7rem;
    border-radius: 6px;
    font-family: monospace;
    font-size: 0.95rem;
    font-weight: 600;
  }

  .habit-count {
    color: #888;
    font-size: 0.9rem;
    margin-left: auto;
  }

  .fortune-box {
    background: linear-gradient(135deg, var(--turquoise-light), var(--sand));
    border-left: 4px solid var(--turquoise);
    border-radius: 8px;
    padding: 1.5rem;
    font-size: 1.1rem;
    color: var(--deep);
    line-height: 1.8;
  }

  .stButton > button {
    background-color: var(--turquoise) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
  }
  .stButton > button:hover {
    background-color: var(--deep) !important;
  }

  .stTextInput > div > div > input {
    border-color: var(--sea-glass) !important;
    border-radius: 8px !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--turquoise) !important;
    box-shadow: 0 0 0 2px rgba(46,191,179,0.2) !important;
  }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def run_analysis(username: str) -> tuple[str, str, int, str]:
    client = ZennClient()

    user = client.get_user(username)
    articles = client.get_all_articles(username)

    if not articles:
        raise ValueError(f"@{username} さんはまだ記事を公開していません。")

    knowledge_map = KnowledgeMap()
    map_html = knowledge_map.build_graph(articles)

    return user.name, user.username, len(articles), map_html


# ヘッダー
st.markdown("<h1>Zenn ブログ分析</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#666;margin-bottom:2rem'>ユーザー名を入力すると、記事から知識地図・口癖・占いを生成します。</p>", unsafe_allow_html=True)

# 入力フォーム
with st.form("analyze_form"):
    username = st.text_input("Zenn ユーザー名", placeholder="例: michan74", label_visibility="collapsed")
    submitted = st.form_submit_button("分析する", type="primary", use_container_width=True)

if submitted:
    if not username.strip():
        st.error("ユーザー名を入力してください。")
    else:
        try:
            with st.spinner(f"@{username} の記事を取得中..."):
                result = run_analysis(username.strip())
            st.session_state["result"] = result
        except ValueError as e:
            st.error(str(e))
        except (ConnectionError, TimeoutError) as e:
            st.error(str(e))
        except RuntimeError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"予期しないエラーが発生しました: {e}")

# 分析結果
if "result" in st.session_state:
    name, username_str, article_count, map_html = st.session_state["result"]

    st.markdown(
        f"<p style='color:#4A7C59;font-weight:600;margin:1rem 0 2rem'>"
        f"{name} さんの記事 {article_count} 件を取得しました"
        f"</p>",
        unsafe_allow_html=True,
    )

    # 知識地図
    st.markdown('<div class="section-card"><div class="section-title">知識地図</div>', unsafe_allow_html=True)
    st.caption("記事タイトルから抽出したキーワードの関係図です。同じ記事に登場したキーワードが近くに集まります。")
    st.components.v1.html(map_html, height=600, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

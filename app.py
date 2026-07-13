import base64
import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

from src.character_diagnosis import CharacterDiagnosis, TRAIT_LABELS, TRAIT_COLORS
from src.models import Article
from src.word_cloud_gen import WordCloudGen
from src.zenn_client import ZennClient

st.set_page_config(page_title="Zenn KUMA診断", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DotGothic16&display=swap');
  :root {
    --turquoise: #2EBFB3;
    --sand: #FAF7F2;
    --sand-dark: #EDE8DF;
    --sea-glass: #8ECFCC;
    --deep: #1A5F7A;
    --gold: #E8B84B;
  }

  .stApp { background-color: var(--sand); }
  header[data-testid="stHeader"] { display: none !important; }
  footer { display: none !important; }

  .block-container {
    max-width: 620px !important;
    padding: 2rem 1.5rem 3rem !important;
  }

  .kuma-title {
    font-family: 'DotGothic16', monospace;
    color: var(--deep);
    font-size: 2rem;
    font-weight: 400;
    text-align: center;
    margin: 1rem 0 0.5rem;
  }

  .section-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--sand-dark);
    box-shadow: 0 2px 8px rgba(26,95,122,0.06);
  }

  .section-title {
    font-family: 'DotGothic16', monospace;
    color: var(--deep);
    font-size: 1rem;
    font-weight: 400;
    border-bottom: 2px solid var(--turquoise);
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
  }

  .bear-name {
    font-family: 'DotGothic16', monospace;
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--deep);
    margin-bottom: 0.8rem;
    line-height: 1.8;
  }

  .trait-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    color: white;
    margin: 0.2rem 0.2rem 0.2rem 0;
  }

  .hearts-row {
    margin-top: 0.8rem;
    line-height: 1.8;
    font-size: 1.2rem;
    word-break: break-all;
    overflow-wrap: anywhere;
  }

  .stButton > button {
    background-color: var(--turquoise) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DotGothic16', monospace !important;
    font-weight: 400 !important;
  }
  .stButton > button:hover { background-color: var(--deep) !important; }

  .stTextInput > div > div > input {
    border-color: var(--sea-glass) !important;
    border-radius: 8px !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--turquoise) !important;
    box-shadow: 0 0 0 2px rgba(46,191,179,0.2) !important;
  }

  code {
    background: var(--sand-dark);
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.82rem;
  }
</style>
""", unsafe_allow_html=True)


def _build_hearts(articles: list[Article]) -> str:
    total = len(articles)
    pub_count = sum(1 for a in articles if a.publication_name)
    normal_count = total - pub_count

    display_max = 30
    overflow = max(0, total - display_max)
    pub_shown = min(pub_count, display_max)
    normal_shown = min(normal_count, display_max - pub_shown)

    hearts = (
        f'<span style="color:#E8B84B">{"♥" * pub_shown}</span>'
        f'<span style="color:#2EBFB3">{"♥" * normal_shown}</span>'
    )
    if overflow:
        hearts += f' <span style="color:#888;font-size:0.9rem">+{overflow}</span>'
    return hearts


@st.cache_data(show_spinner=False)
def run_analysis(username: str) -> tuple:
    client = ZennClient()
    user = client.get_user(username)
    articles = client.get_all_articles(username)

    if not articles:
        raise ValueError(f"@{username} さんはまだ記事を公開していません。")

    diagnosis = CharacterDiagnosis().diagnose(articles)
    wc_bytes = WordCloudGen().generate(articles)

    return user.name, articles, diagnosis, wc_bytes


st.markdown("<p class='kuma-title'>Zenn KUMA診断</p>", unsafe_allow_html=True)

if "result" not in st.session_state:
    st.markdown("""
<p style='text-align:center;color:#666;margin:0.5rem 0 0.3rem'>Zenn ユーザーIDを入力してね</p>
<p style='text-align:center;color:#999;font-size:0.82rem;margin-bottom:1.8rem'>
  例）<code>https://zenn.dev/michan74</code> のページなら <code>michan74</code>
</p>
""", unsafe_allow_html=True)

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        with st.form("analyze_form"):
            username = st.text_input("", placeholder="例: michan74", label_visibility="collapsed")
            submitted = st.form_submit_button("診断開始", type="primary", use_container_width=True)

    if submitted:
        if not username.strip():
            st.error("ユーザーIDを入力してください。")
        else:
            try:
                with st.spinner(f"@{username} の記事を分析中..."):
                    result = run_analysis(username.strip())
                st.session_state["result"] = (username.strip(), result)
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except (ConnectionError, TimeoutError) as e:
                st.error(str(e))
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"予期しないエラーが発生しました: {e}")

else:
    _uname, (display_name, articles, diagnosis, wc_bytes) = st.session_state["result"]

    st.markdown(
        f"<p style='text-align:center;color:#4A7C59;font-weight:600;margin:0.4rem 0 1.5rem'>"
        f"{display_name} さんの記事 {len(articles)} 件を診断しました"
        f"</p>",
        unsafe_allow_html=True,
    )

    # くま診断カード
    badges_html = "".join(
        f'<span class="trait-badge" style="background:{TRAIT_COLORS.get(t, "#888")}">'
        f'{TRAIT_LABELS.get(t, t)}</span>'
        for t in diagnosis.top_traits
    )
    pub_count = sum(1 for a in articles if a.publication_name)
    legend = (
        f'<p style="color:#888;font-size:0.78rem;margin-top:0.3rem">'
        f'<span style="color:#2EBFB3">♥</span> 通常記事 {len(articles) - pub_count} 件'
        + (f'　<span style="color:#E8B84B">♥</span> Publication {pub_count} 件' if pub_count else "")
        + "</p>"
    )
    st.markdown(f"""
<div class="section-card">
  <div class="section-title">くま診断</div>
  <div style="display:flex;gap:1.5rem;align-items:flex-start">
    <div style="flex-shrink:0">{diagnosis.bear_svg}</div>
    <div style="flex:1;min-width:0">
      <div class="bear-name">{diagnosis.bear_name}</div>
      <div>{badges_html}</div>
      <div class="hearts-row">{_build_hearts(articles)}</div>
      {legend}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ワードクラウド
    wc_b64 = base64.b64encode(wc_bytes).decode()
    st.markdown(f"""
<div class="section-card">
  <div class="section-title">よく使うワード</div>
  <img src="data:image/png;base64,{wc_b64}"
       style="width:100%;max-width:1080px;border-radius:8px;display:block;margin:0 auto"/>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("診断し直す", use_container_width=True):
        del st.session_state["result"]
        st.rerun()

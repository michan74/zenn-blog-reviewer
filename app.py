import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

from src.character_diagnosis import CharacterDiagnosis, DiagnosisResult, TRAIT_LABELS, TRAIT_COLORS
from src.models import Article
from src.word_cloud_gen import WordCloudGen
from src.zenn_client import ZennClient

st.set_page_config(page_title="Zenn ブログ分析", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  :root {
    --turquoise: #2EBFB3;
    --turquoise-light: #E6F7F6;
    --sand: #FAF7F2;
    --sand-dark: #EDE8DF;
    --palm: #4A7C59;
    --sea-glass: #8ECFCC;
    --coral: #D4A574;
    --deep: #1A5F7A;
    --gold: #E8B84B;
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

  .bear-name {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--deep);
    margin-bottom: 0.8rem;
    line-height: 1.4;
  }

  .trait-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    color: white;
    margin: 0.2rem 0.2rem 0.2rem 0;
  }

  .hearts-row {
    margin-top: 1rem;
    line-height: 1.8;
    font-size: 1.3rem;
    word-break: break-all;
    overflow-wrap: anywhere;
  }

  .stButton > button {
    background-color: var(--turquoise) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
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


st.markdown("<h1>Zenn ブログ分析</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#666;margin-bottom:2rem'>Zenn ユーザー名を入力すると、記事からくま診断とワードクラウドを生成します。</p>",
    unsafe_allow_html=True,
)

with st.form("analyze_form"):
    username = st.text_input("Zenn ユーザー名", placeholder="例: michan74", label_visibility="collapsed")
    submitted = st.form_submit_button("分析する", type="primary", use_container_width=True)

if submitted:
    if not username.strip():
        st.error("ユーザー名を入力してください。")
    else:
        try:
            with st.spinner(f"@{username} の記事を分析中..."):
                result = run_analysis(username.strip())
            st.session_state["result"] = (username.strip(), result)
        except ValueError as e:
            st.error(str(e))
        except (ConnectionError, TimeoutError) as e:
            st.error(str(e))
        except RuntimeError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"予期しないエラーが発生しました: {e}")

if "result" in st.session_state:
    _uname, (display_name, articles, diagnosis, wc_bytes) = st.session_state["result"]

    st.markdown(
        f"<p style='color:#4A7C59;font-weight:600;margin:1rem 0 2rem'>"
        f"{display_name} さんの記事 {len(articles)} 件を取得しました"
        f"</p>",
        unsafe_allow_html=True,
    )

    # くま診断カード
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">くま診断</div>', unsafe_allow_html=True)

    col_bear, col_info = st.columns([1, 2])

    with col_bear:
        st.markdown(diagnosis.bear_svg, unsafe_allow_html=True)

    with col_info:
        st.markdown(f'<div class="bear-name">{diagnosis.bear_name}</div>', unsafe_allow_html=True)

        badges_html = ""
        for trait in diagnosis.top_traits:
            color = TRAIT_COLORS.get(trait, "#888888")
            label = TRAIT_LABELS.get(trait, trait)
            badges_html += f'<span class="trait-badge" style="background:{color}">{label}</span>'
        st.markdown(badges_html, unsafe_allow_html=True)

        hearts_html = f'<div class="hearts-row">{_build_hearts(articles)}</div>'
        pub_count = sum(1 for a in articles if a.publication_name)
        legend = (
            f'<p style="color:#888;font-size:0.8rem;margin-top:0.3rem">'
            f'<span style="color:#2EBFB3">♥</span> 通常記事 {len(articles) - pub_count} 件'
            + (f'　<span style="color:#E8B84B">♥</span> Publication {pub_count} 件' if pub_count else "")
            + "</p>"
        )
        st.markdown(hearts_html + legend, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ワードクラウド
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">よく使うワード</div>', unsafe_allow_html=True)
    st.image(wc_bytes, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

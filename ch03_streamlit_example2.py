import streamlit as st
from google import genai
from datetime import datetime
import base64


# ============================================
# 기본 설정
# ============================================

st.set_page_config(
    page_title="Gemini 음성비서",
    page_icon="🎤"
)

st.title("🎤 Gemini 음성비서")


# ============================================
# Gemini API
# ============================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================
# session_state 초기화
# ============================================

if "chat" not in st.session_state:
    st.session_state["chat"] = []

if "check_reset" not in st.session_state:
    st.session_state["check_reset"] = False


# ============================================
# 기능 구현 공간
# ============================================

col1, col2 = st.columns(2)


with col1:

    audio = st.audio_input(
        "🎙️ 질문을 말씀해주세요",
        sample_rate=16000
    )


with col2:

    if st.button("대화 초기화"):

        st.session_state["chat"] = []
        st.session_state["check_reset"] = True

        st.rerun()


# ============================================
# 음성 입력 처리
# ============================================

if audio is not None:

    st.session_state["check_reset"] = False

    # 녹음 음성 재생
    st.audio(
        audio.getvalue(),
        format="audio/wav"
    )

    # 음성 데이터
    audio_bytes = audio.getvalue()

    audio_base64 = base64.b64encode(
        audio_bytes
    ).decode("utf-8")


    # ========================================
    # Gemini에게 음성 전달
    # ========================================

    with st.spinner("Gemini가 듣고 있습니다..."):

        interaction = client.interactions.create(

            model="gemini-3.6-flash",

            input=[

                {
                    "type": "text",
                    "text": """
                    당신은 한국어 AI 음성비서입니다.

                    사용자의 음성을 이해한 뒤
                    다음 형식으로 응답하세요.

                    질문: 사용자가 말한 내용을 텍스트로 작성
                    답변: 질문에 대한 자연스러운 한국어 답변

                    답변은 간결하게 작성하세요.
                    """
                },

                {
                    "type": "audio",
                    "data": audio_base64,
                    "mime_type": "audio/wav"
                }
            ]
        )


    result = interaction.output_text


    # ========================================
    # 시간
    # ========================================

    now = datetime.now().strftime("%H:%M")


    # ========================================
    # 채팅 기록 저장
    # ========================================

    st.session_state["chat"].append(
        (
            "user",
            "🎤 음성 질문",
            now
        )
    )

    st.session_state["chat"].append(
        (
            "assistant",
            result,
            now
        )
    )


# ============================================
# 채팅 화면
# ============================================

st.divider()

st.subheader("💬 대화 내용")


for role, message, time in st.session_state["chat"]:

    if role == "user":

        with st.chat_message("user"):

            st.write(message)
            st.caption(time)

    else:

        with st.chat_message("assistant"):

            st.write(message)
            st.caption(time)
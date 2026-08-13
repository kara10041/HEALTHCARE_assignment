import streamlit as st
from google import genai
from datetime import datetime
import base64
import hashlib


# ============================================
# 기본 설정
# ============================================

st.set_page_config(
    page_title="AI 음성비서",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 AI 음성비서")


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

# 같은 녹음 파일이 rerun될 때 중복 처리되는 것 방지
if "last_audio_hash" not in st.session_state:
    st.session_state["last_audio_hash"] = None


# ============================================
# 사이드바 - 모델 선택
# ============================================

with st.sidebar:

    st.header("⚙️ 설정")

    st.subheader("AI 모델")

    model_option = st.radio(
        "사용할 모델을 선택하세요.",
        [
            "Gemini 3.6 Flash",
            "Gemini 3.5 Flash-Lite"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("현재 선택된 모델")
    st.write(f"🤖 {model_option}")

    st.divider()

    if st.button(
        "🔄 대화 초기화",
        use_container_width=True
    ):
        st.session_state["chat"] = []
        st.session_state["check_reset"] = True
        st.session_state["last_audio_hash"] = None

        st.rerun()


# ============================================
# 화면 표시 이름 → 실제 Gemini 모델명
# ============================================

MODEL_MAP = {
    "Gemini 3.6 Flash": "gemini-3.6-flash",
    "Gemini 3.5 Flash-Lite": "gemini-3.5-flash-lite"
}

selected_model = MODEL_MAP[model_option]


# ============================================
# 프로그램 안내
# ============================================

with st.expander("📌 음성비서 프로그램에 관하여"):

    st.markdown(
        """
        - 음성을 녹음하여 AI에게 질문할 수 있습니다.
        - Gemini의 멀티모달 기능을 이용해 음성을 인식합니다.
        - **Gemini 3.6 Flash / Gemini 3.5 Flash-Lite** 중
          사용할 모델을 직접 선택할 수 있습니다.
        - 질문 내용과 AI의 답변은 아래 대화 화면에 표시됩니다.
        """
    )


# ============================================
# 기능 구현 공간
# ============================================

st.divider()

col1, col2 = st.columns([1, 1])


with col1:

    st.subheader("🎙️ 질문하기")

    audio = st.audio_input(
        "질문을 말씀해주세요",
        sample_rate=16000
    )


with col2:

    st.subheader("🤖 현재 설정")

    st.info(
        f"""
        **선택된 AI 모델**

        {model_option}
        """
    )


# ============================================
# 음성 입력 처리
# ============================================

if audio is not None:

    st.session_state["check_reset"] = False

    # 음성 데이터
    audio_bytes = audio.getvalue()

    # 현재 녹음 데이터 고유값 생성
    current_audio_hash = hashlib.md5(
        audio_bytes
    ).hexdigest()


    # ========================================
    # 같은 음성을 중복 처리하지 않도록 확인
    # ========================================

    if current_audio_hash != st.session_state["last_audio_hash"]:

        st.session_state["last_audio_hash"] = current_audio_hash


        # 녹음 음성 재생
        st.audio(
            audio_bytes,
            format="audio/wav"
        )


        # Base64 변환
        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode("utf-8")


        # ====================================
        # Gemini에게 음성 전달
        # ====================================

        with st.spinner(
            f"{model_option}이(가) 음성을 분석하고 있습니다..."
        ):

            try:

                interaction = client.interactions.create(

                    model=selected_model,

                    input=[

                        {
                            "type": "text",
                            "text": """
당신은 한국어 AI 음성비서입니다.

사용자의 음성을 정확하게 이해한 뒤
다음 형식으로 응답하세요.

질문: 사용자가 말한 내용을 텍스트로 작성
답변: 질문에 대한 자연스러운 한국어 답변

답변은 이해하기 쉽고 간결하게 작성하세요.
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


                # ============================
                # 시간
                # ============================

                now = datetime.now().strftime("%H:%M")


                # ============================
                # 채팅 기록 저장
                # ============================

                st.session_state["chat"].append(
                    (
                        "user",
                        "🎤 음성 질문",
                        now,
                        model_option
                    )
                )

                st.session_state["chat"].append(
                    (
                        "assistant",
                        result,
                        now,
                        model_option
                    )
                )


            except Exception as e:

                st.error(
                    f"AI 응답 중 오류가 발생했습니다.\n\n{e}"
                )


# ============================================
# 채팅 화면
# ============================================

st.divider()

st.subheader("💬 질문 / 답변")


if len(st.session_state["chat"]) == 0:

    st.info(
        "아직 대화 내용이 없습니다. "
        "위에서 음성을 녹음해 질문해보세요."
    )


for role, message, time, used_model in st.session_state["chat"]:

    if role == "user":

        with st.chat_message("user"):

            st.write(message)
            st.caption(time)

    else:

        with st.chat_message("assistant"):

            st.write(message)

            st.caption(
                f"{time} · {used_model}"
            )

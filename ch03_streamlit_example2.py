import streamlit as st
from google import genai
from datetime import datetime
import base64
import hashlib
import io
import wave


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
# TTS 설정
# ============================================

# Gemini 공식 TTS 전용 모델
TTS_MODEL = "gemini-3.1-flash-tts-preview"

# 기본 음성
TTS_VOICE = "Kore"


# ============================================
# PCM → WAV 변환 함수
# ============================================

def pcm_to_wav_bytes(
    pcm_data,
    sample_rate=24000,
    channels=1,
    sample_width=2
):
    """
    Gemini TTS에서 반환된 PCM 데이터를
    Streamlit에서 재생 가능한 WAV bytes로 변환
    """

    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, "wb") as wf:

        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)

    return wav_buffer.getvalue()


# ============================================
# Gemini 답변에서 '답변:' 부분만 추출
# ============================================

def extract_answer_text(result):

    if "답변:" in result:

        return result.split(
            "답변:",
            1
        )[1].strip()

    return result.strip()


# ============================================
# TTS 생성 함수
# ============================================

def generate_tts(text):

    tts_interaction = client.interactions.create(

        model=TTS_MODEL,

        input=f"""
다음 한국어 답변을 자연스럽고 편안한
AI 음성비서의 목소리로 읽어주세요.

너무 빠르지 않게 말하고,
질문에 답해주는 자연스러운 말투를 사용하세요.

{text}
""",

        response_format={
            "type": "audio"
        },

        generation_config={
            "speech_config": [
                {
                    "voice": TTS_VOICE
                }
            ]
        }
    )

    audio_data = tts_interaction.output_audio.data

    # SDK 버전에 따라 str / bytes 모두 대응
    if isinstance(audio_data, str):

        pcm_data = base64.b64decode(
            audio_data
        )

    else:

        pcm_data = audio_data

    wav_bytes = pcm_to_wav_bytes(
        pcm_data
    )

    return wav_bytes


# ============================================
# session_state 초기화
# ============================================

if "chat" not in st.session_state:
    st.session_state["chat"] = []

if "check_reset" not in st.session_state:
    st.session_state["check_reset"] = False

# 같은 녹음 파일이 rerun될 때
# 중복 처리되는 것 방지
if "last_audio_hash" not in st.session_state:
    st.session_state["last_audio_hash"] = None


# ============================================
# 이번 실행에서만 자동재생할지 여부
# ============================================

autoplay_new_tts = False


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

    # ========================================
    # TTS 설정
    # ========================================

    st.subheader("🔊 음성 답변")

    tts_enabled = st.toggle(
        "답변을 음성으로 생성",
        value=True
    )

    autoplay_enabled = st.toggle(
        "새 답변 자동 재생",
        value=True,
        disabled=not tts_enabled
    )

    st.caption(
        "음성 출력: Gemini 3.1 Flash TTS"
    )

    st.divider()

    st.caption("현재 선택된 모델")

    st.write(
        f"🤖 {model_option}"
    )

    if tts_enabled:

        st.write(
            f"🔊 TTS: {TTS_VOICE}"
        )

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

    "Gemini 3.6 Flash":
        "gemini-3.6-flash",

    "Gemini 3.5 Flash-Lite":
        "gemini-3.5-flash-lite"
}

selected_model = MODEL_MAP[
    model_option
]


# ============================================
# 프로그램 안내
# ============================================

with st.expander(
    "📌 음성비서 프로그램에 관하여"
):

    st.markdown(
        """
        - 음성을 녹음하여 AI에게 질문할 수 있습니다.
        - Gemini의 멀티모달 기능을 이용해 음성을 인식합니다.
        - **Gemini 3.6 Flash / Gemini 3.5 Flash-Lite** 중
          사용할 모델을 직접 선택할 수 있습니다.
        - AI의 텍스트 답변을 **음성으로도 들을 수 있습니다.**
        - 질문 내용과 AI의 답변은 아래 대화 화면에 표시됩니다.
        """
    )


# ============================================
# 기능 구현 공간
# ============================================

st.divider()

col1, col2 = st.columns(
    [1, 1]
)


with col1:

    st.subheader(
        "🎙️ 질문하기"
    )

    audio = st.audio_input(
        "질문을 말씀해주세요",
        sample_rate=16000
    )


with col2:

    st.subheader(
        "🤖 현재 설정"
    )

    tts_status = (
        "사용"
        if tts_enabled
        else "사용 안 함"
    )

    st.info(
        f"""
        **선택된 AI 모델**

        {model_option}

        **음성 답변**

        {tts_status}
        """
    )


# ============================================
# 음성 입력 처리
# ============================================

if audio is not None:

    st.session_state[
        "check_reset"
    ] = False

    # ========================================
    # 음성 데이터
    # ========================================

    audio_bytes = audio.getvalue()

    # 현재 녹음 데이터 고유값 생성
    current_audio_hash = hashlib.md5(
        audio_bytes
    ).hexdigest()


    # ========================================
    # 같은 음성을 중복 처리하지 않도록 확인
    # ========================================

    if (
        current_audio_hash
        != st.session_state[
            "last_audio_hash"
        ]
    ):

        st.session_state[
            "last_audio_hash"
        ] = current_audio_hash


        # ====================================
        # 녹음 음성 재생
        # ====================================

        st.audio(
            audio_bytes,
            format="audio/wav"
        )


        # ====================================
        # Base64 변환
        # ====================================

        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode(
            "utf-8"
        )


        # ====================================
        # Gemini에게 음성 전달
        # ====================================

        with st.spinner(
            f"{model_option}이(가) "
            "음성을 분석하고 있습니다..."
        ):

            try:

                interaction = (
                    client.interactions.create(

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
                                "mime_type":
                                    "audio/wav"
                            }
                        ]
                    )
                )


                result = (
                    interaction.output_text
                )


                # ============================
                # 시간
                # ============================

                now = (
                    datetime.now()
                    .strftime("%H:%M")
                )


                # ============================
                # TTS 생성
                # ============================

                tts_audio = None

                if tts_enabled:

                    # "질문:"까지 읽지 않고
                    # 실제 답변만 음성으로 생성
                    answer_text = (
                        extract_answer_text(
                            result
                        )
                    )

                    try:

                        with st.spinner(
                            "🔊 음성 답변을 "
                            "생성하고 있습니다..."
                        ):

                            tts_audio = (
                                generate_tts(
                                    answer_text
                                )
                            )

                            autoplay_new_tts = (
                                autoplay_enabled
                            )

                    except Exception as tts_error:

                        # TTS 실패해도
                        # 기존 텍스트 답변은 정상 유지
                        st.warning(
                            "텍스트 답변은 "
                            "정상적으로 생성되었지만 "
                            "음성 생성에 실패했습니다."
                            f"\n\n{tts_error}"
                        )


                # ============================
                # 채팅 기록 저장
                # ============================

                st.session_state[
                    "chat"
                ].append(
                    (
                        "user",
                        "🎤 음성 질문",
                        now,
                        model_option,
                        None
                    )
                )


                st.session_state[
                    "chat"
                ].append(
                    (
                        "assistant",
                        result,
                        now,
                        model_option,
                        tts_audio
                    )
                )


            except Exception as e:

                st.error(
                    "AI 응답 중 오류가 "
                    "발생했습니다."
                    f"\n\n{e}"
                )


# ============================================
# 채팅 화면
# ============================================

st.divider()

st.subheader(
    "💬 질문 / 답변"
)


if len(
    st.session_state["chat"]
) == 0:

    st.info(
        "아직 대화 내용이 없습니다. "
        "위에서 음성을 녹음해 질문해보세요."
    )


# ============================================
# 채팅 기록 표시
# ============================================

chat_length = len(
    st.session_state["chat"]
)


for index, chat_item in enumerate(
    st.session_state["chat"]
):

    # ========================================
    # 이전 버전 4개 tuple도 호환
    # ========================================

    if len(chat_item) == 4:

        role, message, time, used_model = (
            chat_item
        )

        tts_audio = None

    else:

        (
            role,
            message,
            time,
            used_model,
            tts_audio
        ) = chat_item


    # ========================================
    # 사용자 메시지
    # ========================================

    if role == "user":

        with st.chat_message(
            "user"
        ):

            st.write(
                message
            )

            st.caption(
                time
            )


    # ========================================
    # AI 메시지
    # ========================================

    else:

        with st.chat_message(
            "assistant"
        ):

            st.write(
                message
            )

            st.caption(
                f"{time} · "
                f"{used_model}"
            )


            # =================================
            # TTS 오디오
            # =================================

            if tts_audio is not None:

                # 새로 생성된 마지막 답변만
                # 한 번 자동재생
                is_latest_message = (
                    index
                    == chat_length - 1
                )

                st.audio(
                    tts_audio,
                    format="audio/wav",
                    autoplay=(
                        autoplay_new_tts
                        and is_latest_message
                    )
                )
        

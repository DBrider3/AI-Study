import os
import base64
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# .env 파일에서 환경변수 불러오기
load_dotenv()

def load_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
    


# 앱 제목 설정하기
st.title("소비 패턴 기반 패션 추천 서비스")

# OpenAI 모델 초기화 (스트리밍 모드 활성화)
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)

# ===== 세션 상태 초기화 =====
# 대화 내역을 저장할 리스트 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이미지 업로드 상태 체크 (True: 업로드 완료, False: 미완료)
if "images_uploaded" not in st.session_state:
    st.session_state.images_uploaded = False

# ===== 이전 대화 표시하기 =====
# 저장된 대화 내역을 화면에 보여주기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===== 이미지 업로드 섹션 =====
# 아직 이미지가 업로드되지 않았다면 업로드 UI 표시
if not st.session_state.images_uploaded:
    st.write("먼저 본인의 전신이 보이는 사진을 올려주세요!")
    # 전신 사진 업로드 받기
    person_image = st.file_uploader(
        "전신 사진", type=["png", "jpg", "jpeg"], key="person"
    )

    # 전신 사진이 업로드되면 화면에 표시하고 옷 사진 업로드 UI 보여주기
    if person_image:
        st.image(person_image, caption="전신 사진")

        st.write("이제 사고 싶은 옷들의 사진을 올려주세요!")
        # 여러 장의 옷 사진 업로드 받기
        clothes_images = st.file_uploader(
            "사고 싶은 옷 사진들",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="clothes",
        )

        # 옷 사진들 표시하기
        if clothes_images:
            for i, cloth_img in enumerate(clothes_images):
                st.image(cloth_img, caption=f"옷 {i+1}")

            # 대화 시작 버튼
            if st.button("대화 시작하기"):
                # 이미지들을 세션 상태에 저장해서 채팅 중에도 접근 가능하게 하기
                st.session_state.person_image = person_image
                st.session_state.clothes_images = clothes_images
                st.session_state.images_uploaded = True

                # AI의 첫 인사말 추가하기
                initial_message = "안녕하세요! 패션 추천 봇입니다. 업로드해주신 사진들을 분석해 드릴게요. 어떤 스타일을 찾고 계신가요? 또는 특별한 날을 위한 옷을 찾고 계신가요?"
                st.session_state.messages.append(
                    {"role": "assistant", "content": initial_message}
                )
                # 페이지 새로고침하여 대화 UI로 전환
                st.rerun()

# ===== 채팅 인터페이스 =====
# 이미지가 업로드된 후에만 채팅 입력창 표시
if st.session_state.images_uploaded:
    # 사용자 입력 받기
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지를 대화 내역에 추가
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 사용자 메시지 화면에 표시
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성 및 표시
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                # 프롬프트 불러오기
                prompt_template = load_prompt("prompt.txt")
                
                # 이미지 인코딩 작업 (base64 형식으로 변환)
                # 전신 사진 인코딩
                person_encoded = base64.b64encode(
                    st.session_state.person_image.read()
                ).decode("utf-8")
                # 파일 포인터 초기화 (다음에 또 읽을 수 있도록)
                st.session_state.person_image.seek(0)

                # 옷 사진들 인코딩
                clothes_encoded = []
                for cloth in st.session_state.clothes_images:
                    clothes_encoded.append(
                        base64.b64encode(cloth.read()).decode("utf-8")
                    )
                    # 각 파일 포인터 초기화
                    cloth.seek(0)

                # 지금까지의 대화 내역을 문자열로 변환
                conversation_history = "\n".join(
                    [
                        f"{msg['role']}: {msg['content']}"
                        for msg in st.session_state.messages
                    ]
                )

                # AI에게 전달할 내용 구성 (프롬프트 + 대화 내역 + 이미지들)
                content = [
                    {
                        "type": "text",
                        "text": f"{prompt_template}\n\n다음은 지금까지의 대화 내용입니다:\n\n{conversation_history}\n\n사용자의 질문에 친절하게 답변해주세요.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{person_encoded}"
                        },
                    },
                ]

                # 옷 이미지들 추가
                for cloth_encoded in clothes_encoded:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{cloth_encoded}"
                            },
                        }
                    )

                # 메시지 생성 및 API 요청 준비
                message = HumanMessage(content=content)
                # 응답을 표시할 빈 공간 생성
                response_placeholder = st.empty()
                full_response = ""

                # 스트리밍 방식으로 응답 받기 (실시간으로 화면에 표시)
                for chunk in model.stream([message]):
                    if chunk.content:
                        full_response += chunk.content
                        response_placeholder.markdown(full_response)

                # AI 응답을 대화 내역에 추가
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

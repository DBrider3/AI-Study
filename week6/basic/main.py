import os
import base64
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# 환경변수 불러오기
load_dotenv()

# 앱 제목 설정
st.title("기본과제 - 이미지 기반 AI 챗봇")
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "images_uploaded" not in st.session_state:
    st.session_state.images_uploaded = False

# 대화 내역 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 이미지 업로드 섹션
if not st.session_state.images_uploaded:
    st.write("질문하고 싶은 이미지들을 업로드해주세요!")

    # 여러 이미지 한번에 업로드 받기
    uploaded_images = st.file_uploader(
        "이미지 파일들",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="images",
    )

    # 업로드된 이미지 표시
    if uploaded_images and len(uploaded_images) > 0:
        # 이미지 미리보기
        for i, img in enumerate(uploaded_images):
            st.image(img, caption=f"이미지 {i+1}", width=200)

        # 대화 시작 버튼
        if st.button("대화 시작하기"):
            # 이미지들을 세션 상태에 저장해서 대화 중에도 접근 가능하게 하기
            st.session_state.uploaded_images = uploaded_images
            st.session_state.images_uploaded = True

            # 초기 메시지
            initial_message = "안녕하세요! 업로드하신 이미지들에 대해 질문해 주세요."
            st.session_state.messages.append(
                {"role": "assistant", "content": initial_message}
            )
            st.rerun()

# 채팅 인터페이스
if st.session_state.images_uploaded:
    # 사용자 입력 받기
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 대화 내역에 추가
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 사용자 메시지 화면에 표시
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성 및 표시
        with st.chat_message("assistant"):
            with st.spinner("이미지 분석 중..."):
                # 이미지 인코딩 (base64)
                images_encoded = []
                for img in st.session_state.uploaded_images:
                    images_encoded.append(base64.b64encode(img.read()).decode("utf-8"))
                    img.seek(0)  # 파일 포인터 초기화

                # 이전 대화 내역 문자열로 변환
                conversation_history = "\n".join(
                    [
                        f"{msg['role']}: {msg['content']}"
                        for msg in st.session_state.messages
                    ]
                )

                # AI에게 전달할 내용 구성 (텍스트 + 이미지들)
                content = [
                    {
                        "type": "text",
                        "text": f"다음은 사용자가 업로드한 이미지들과 지금까지의 대화 내용입니다. 이미지를 참조하여 사용자의 질문에 답변해주세요:\n\n{conversation_history}",
                    }
                ]

                # 이미지들 추가
                for img_encoded in images_encoded:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_encoded}"
                            },
                        }
                    )

                # 메시지 생성 및 API 요청
                message = HumanMessage(content=content)
                response_placeholder = st.empty()
                full_response = ""

                # 스트리밍 응답
                for chunk in model.stream([message]):
                    if chunk.content:
                        full_response += chunk.content
                        response_placeholder.markdown(full_response)

                # AI 응답을 대화 내역에 추가
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

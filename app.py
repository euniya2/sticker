import streamlit as st
import requests
import json
import io
from PIL import Image
import base64

# 1. 페이지 설정
st.set_page_config(page_title="AI 칭찬 스티커 생성기", layout="centered")

st.title("🎨 AI 맞춤형 칭찬 스티커 생성기")
st.write("학생의 긍정적 행동을 입력하면 AI가 교육적인 칭찬 스티커를 제작합니다.")

# 2. 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Google API Key를 입력하세요", type="password")
    st.info("Google AI Studio에서 발급받은 키를 입력해 주세요.")
    st.markdown("[API 키 발급받기](https://aistudio.google.com/app/apikey)")

# 3. 메인 입력창
praise_text = st.text_area("학생에 대한 칭찬 내용을 입력하세요", 
                          placeholder="예: 친구들의 책상 정리를 스스로 도와줌",
                          help="칭찬 내용을 바탕으로 AI가 캐릭터 테마를 결정합니다.")

# 4. 이미지 생성 함수 (REST API 직접 호출 방식 - 버전 오류 없음)
def generate_image_api(api_key, prompt):
    # Imagen 4 모델 API 엔드포인트
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        # base64 이미지 데이터 추출
        img_b64 = result['predictions'][0]['bytesBase64Encoded']
        return base64.b64decode(img_b64)
    else:
        raise Exception(f"API 에러 ({response.status_code}): {response.text}")

# 5. 실행 로직
if st.button("칭찬 스티커 만들기"):
    if not api_key:
        st.error("먼저 사이드바에 Google API Key를 입력해 주세요!")
    elif not praise_text:
        st.warning("칭찬 내용을 입력해 주세요.")
    else:
        try:
            # 스티커용 프롬프트 구성
            image_prompt = f"A cute and friendly 3D cartoon character sticker for a student who {praise_text}. White background, vibrant colors, clean sticker style with a thick white border, high resolution, centered composition."
            
            with st.spinner('AI가 구글 서버에 직접 접속하여 스티커를 그리고 있습니다...'):
                # API 직접 호출
                image_bytes = generate_image_api(api_key, image_prompt)
                
                if image_bytes:
                    st.success("교육용 칭찬 스티커가 완성되었습니다!")
                    
                    # 카드 스타일 UI
                    st.markdown(f"""
                    <div style="background-color: white; padding: 25px; border-radius: 20px; border: 4px dashed #FFD700; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px;">
                        <h2 style="color: #FF4B4B; margin: 0;">✨ 참 잘했어요! ✨</h2>
                        <hr style="border: 0.5px solid #eee; margin: 15px 0;">
                        <p style="font-size: 1.3rem; color: #444; line-height: 1.6;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 이미지 표시
                    final_img = Image.open(io.BytesIO(image_bytes))
                    st.image(final_img, use_column_width=True)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="💾 스티커 이미지 저장하기",
                        data=image_bytes,
                        file_name="praise_sticker.png",
                        mime="image/png"
                    )

        except Exception as e:
            st.error(f"생성 중 오류 발생: {str(e)}")
            st.info("💡 힌트: 입력하신 API Key가 Imagen 4 모델을 지원하는지 Google AI Studio에서 확인해 주세요.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Imagen 4 직접 연결 버전")

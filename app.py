import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 페이지 설정
st.set_page_config(page_title="AI 칭찬 스티커 생성기", layout="centered")

st.title("🎨 AI 맞춤형 칭찬 스티커 생성기")
st.write("학생의 잘한 점을 입력하면 AI가 귀여운 캐릭터 스티커를 만들어 줍니다!")

# 사이드바 설정 (API Key 입력)
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Google API Key를 입력하세요", type="password")
    st.info("Google AI Studio에서 발급받은 키를 입력해 주세요.")
    st.markdown("[API 키 발급받기](https://aistudio.google.com/app/apikey)")

# 메인 입력창
praise_text = st.text_area("학생에 대한 칭찬 내용을 입력하세요", 
                          placeholder="예: 발표를 용기 있게 함, 친구를 배려하고 도와줌",
                          help="칭찬 내용을 바탕으로 AI가 캐릭터 테마를 결정합니다.")

if st.button("칭찬 스티커 만들기"):
    if not api_key:
        st.error("먼저 사이드바에 Google API Key를 입력해 주세요!")
    elif not praise_text:
        st.warning("칭찬 내용을 입력해 주세요.")
    else:
        try:
            # Gemini Imagen 모델 설정
            genai.configure(api_key=api_key)
            
            # 이미지 생성을 위한 프롬프트 구성
            # Imagen 3를 위한 최적화된 프롬프트
            image_prompt = f"A cute and friendly cartoon character sticker for a student who {praise_text}. The character should look happy and encouraging. Sticker style, white background, bright colors, 3D render style, high resolution, center aligned."
            
            with st.spinner('AI가 맞춤형 스티커를 그리고 있습니다... (약 10~20초 소요)'):
                # Imagen 3 모델 사용
                model = genai.GenerativeModel(model_name='imagen-3.0-generate-001')
                
                # 이미지 생성 호출
                response = model.generate_content(image_prompt)
                
                if response:
                    st.success("짜잔! 스티커가 완성되었습니다.")
                    
                    # 스티커 카드 디자인 (UI 시각화)
                    st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1);">
                        <h2 style="color: #FF4B4B;">🌟 참 잘했어요! 🌟</h2>
                        <p style="font-size: 1.2rem; color: #333;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 이미지 표시 로직
                    # 응답의 parts[0]에 이미지 데이터가 담겨 옵니다.
                    img_data = response.candidates[0].content.parts[0].inline_data.data
                    image = Image.open(io.BytesIO(img_data))
                    st.image(image, use_column_width=True)
                    
                    # 다운로드 버튼
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="스티커 다운로드하기",
                        data=byte_im,
                        file_name="praise_sticker.png",
                        mime="image/png"
                    )
                else:
                    st.error("이미지를 생성하지 못했습니다. 다시 시도해 주세요.")
                    
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("힌트: Google AI Studio에서 Imagen 모델 접근 권한(무료 티어)을 확인해 보세요.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Gemini Imagen 3")

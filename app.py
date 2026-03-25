import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 페이지 설정
st.set_page_config(page_title="AI 칭찬 스티커 생성기", layout="centered")

st.title("🎨 AI 맞춤형 칭찬 스티커 생성기")
st.write("학생의 잘한 점을 입력하면 AI가 귀여운 캐릭터 스티커를 만들어 줍니다!")

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Google API Key를 입력하세요", type="password")
    st.info("Google AI Studio에서 발급받은 키를 입력해 주세요.")
    st.markdown("[API 키 발급받기](https://aistudio.google.com/app/apikey)")

# 메인 입력창
praise_text = st.text_area("학생에 대한 칭찬 내용을 입력하세요", 
                          placeholder="예: 발표를 너무 잘했음, 친구를 배려함")

if st.button("칭찬 스티커 만들기"):
    if not api_key:
        st.error("먼저 사이드바에 Google API Key를 입력해 주세요!")
    elif not praise_text:
        st.warning("칭찬 내용을 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            image_prompt = f"A cute 3D cartoon character sticker for a student who {praise_text}. White background, vibrant colors, sticker style, high quality, centered."
            
            with st.spinner('AI가 스티커를 그리고 있습니다...'):
                # 호출 시도 1: 최신 ImageGenerationModel 방식
                try:
                    if hasattr(genai, 'ImageGenerationModel'):
                        model = genai.ImageGenerationModel('imagen-4.0-generate-001')
                        result = model.generate_images(prompt=image_prompt, number_of_images=1)
                        img = result.images[0]
                    else:
                        # 호출 시도 2: 도구가 없을 경우 직접 모델명으로 호출
                        model = genai.get_model('models/imagen-4.0-generate-001')
                        # 일부 버전에서는 generate_images가 model 객체에 바로 붙어있음
                        result = model.generate_images(prompt=image_prompt)
                        img = result.images[0]
                except Exception as inner_e:
                    # 호출 시도 3: 위 방식이 모두 실패할 경우 최후의 수단
                    st.warning("최신 호출 방식을 시도 중입니다...")
                    model = genai.get_model('models/imagen-3.0-generate-001')
                    result = model.generate_images(prompt=image_prompt)
                    img = result.images[0]

                if img:
                    st.success("스티커가 완성되었습니다!")
                    st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                        <h2 style="color: #FF4B4B; margin: 0;">🌟 참 잘했어요! 🌟</h2>
                        <p style="font-size: 1.2rem; color: #333; margin-top: 10px;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    display_img = img._pil_image if hasattr(img, '_pil_image') else img
                    st.image(display_img, use_column_width=True)
                    
                    buf = io.BytesIO()
                    display_img.save(buf, format="PNG")
                    st.download_button(label="스티커 다운로드", data=buf.getvalue(), file_name="sticker.png", mime="image/png")

        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            st.info("💡 만약 'ImageGenerationModel' 관련 에러가 계속된다면, Streamlit Cloud 대시보드에서 앱을 'Delete' 한 후 다시 'New app'으로 배포해 보세요.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Imagen 대응")

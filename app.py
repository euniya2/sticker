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
            
            with st.spinner('AI가 내 계정의 모델을 확인하고 스티커를 그리는 중입니다...'):
                
                # 1. 내 계정에서 사용 가능한 Imagen 모델 이름 자동으로 찾기
                available_models = [m.name for m in genai.list_models() if 'imagen' in m.name]
                
                if not available_models:
                    # 만약 이름에 imagen이 없다면 gemini-3.1-flash-image 등 검색
                    available_models = [m.name for m in genai.list_models() if 'image' in m.name]

                if not available_models:
                    st.error("사용 가능한 이미지 생성 모델을 찾을 수 없습니다. API 키의 권한을 확인해 주세요.")
                    st.stop()

                # 2. 찾은 모델 중 가장 최신 버전(보통 리스트의 뒤쪽)부터 시도
                target_model = available_models[-1] 
                st.caption(f"🚀 {target_model} 모델로 생성을 시도합니다.")

                # 3. 이미지 생성 실행
                # 최신 SDK의 ImageGenerationModel 방식 우선 시도
                if hasattr(genai, 'ImageGenerationModel'):
                    # 모델 이름에서 'models/' 접두사 제거 (필요한 경우)
                    clean_name = target_model.replace('models/', '')
                    model = genai.ImageGenerationModel(clean_name)
                    result = model.generate_images(prompt=image_prompt, number_of_images=1)
                    img_obj = result.images[0]
                else:
                    # 구형 방식 시도
                    model = genai.get_model(target_model)
                    result = model.generate_images(prompt=image_prompt)
                    img_obj = result.images[0]

                if img_obj:
                    st.success("스티커가 완성되었습니다!")
                    st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                        <h2 style="color: #FF4B4B; margin: 0;">🌟 참 잘했어요! 🌟</h2>
                        <p style="font-size: 1.2rem; color: #333; margin-top: 10px;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 이미지 변환 및 표시
                    display_img = img_obj._pil_image if hasattr(img_obj, '_pil_image') else img_obj
                    st.image(display_img, use_column_width=True)
                    
                    # 다운로드 버튼
                    buf = io.BytesIO()
                    display_img.save(buf, format="PNG")
                    st.download_button(label="스티커 다운로드", data=buf.getvalue(), file_name="sticker.png", mime="image/png")

        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            st.info("💡 사용 가능한 모델 목록: " + ", ".join([m.name for m in genai.list_models() if 'image' in m.name]))

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - 자동 모델 탐색 버전")

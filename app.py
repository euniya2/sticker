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
                          placeholder="예: 발표를 너무 잘했음, 친구를 배려함",
                          help="칭찬 내용을 바탕으로 AI가 캐릭터 테마를 결정합니다.")

if st.button("칭찬 스티커 만들기"):
    if not api_key:
        st.error("먼저 사이드바에 Google API Key를 입력해 주세요!")
    elif not praise_text:
        st.warning("칭찬 내용을 입력해 주세요.")
    else:
        try:
            # Gemini API 설정
            genai.configure(api_key=api_key)
            
            # 이미지 생성을 위한 프롬프트 구성
            image_prompt = f"A cute and friendly 3D cartoon character sticker for a student who {praise_text}. White background, vibrant colors, sticker style with a thick white border, high quality, centered."
            
            with st.spinner('AI가 최신 Imagen 4 모델로 스티커를 그리고 있습니다... (약 10~20초 소요)'):
                # 💡 스크린샷에서 확인된 최신 모델명으로 수정
                # 'imagen-4.0-generate-001' 또는 'gemini-2.5-flash-image' 사용 가능
                model_name = 'models/imagen-4.0-generate-001'
                imagen = genai.get_model(model_name)
                
                # 이미지 생성 실행
                result = imagen.generate_images(
                    prompt=image_prompt,
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="block_some",
                    person_generation="allow_adult"
                )
                
                if result and result.images:
                    st.success("짜잔! 최신 모델로 스티커가 완성되었습니다.")
                    
                    # 스티커 카드 디자인
                    st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                        <h2 style="color: #FF4B4B; margin: 0;">🌟 참 잘했어요! 🌟</h2>
                        <p style="font-size: 1.2rem; color: #333; margin-top: 10px;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 생성된 이미지 표시
                    generated_image = result.images[0]
                    # 이미지가 PIL Image 객체인 경우 _pil_image 사용
                    if hasattr(generated_image, '_pil_image'):
                        st.image(generated_image._pil_image, use_column_width=True)
                        
                        # 다운로드 버튼 준비
                        buf = io.BytesIO()
                        generated_image._pil_image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                    else:
                        st.image(generated_image, use_column_width=True)
                        # 바이트 데이터인 경우 처리
                        byte_im = generated_image
                    
                    st.download_button(
                        label="스티커 다운로드하기",
                        data=byte_im,
                        file_name="praise_sticker.png",
                        mime="image/png"
                    )
                else:
                    st.error("이미지를 생성하지 못했습니다. Google AI Studio에서 모델 권한을 다시 확인해 보세요.")
                    
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("💡 힌트: 스크린샷에 보이는 'Imagen 4' 또는 'Nano Banana' 모델명을 코드의 model_name 변수에 정확히 입력했는지 확인해 보세요.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Imagen 4 적용 버전")

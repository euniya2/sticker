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
            
            # 💡 수정된 부분: 이미지 생성 전용 모델 호출 방식
            # Imagen 3 모델은 GenerativeModel이 아닌 별도의 방식으로 호출될 수 있습니다.
            # 최신 SDK 기준으로는 아래와 같은 방식을 권장합니다.
            
            image_prompt = f"A cute and friendly 3D cartoon character sticker for a student who {praise_text}. White background, vibrant colors, sticker style with a thick white border, high quality, centered."
            
            with st.spinner('AI가 맞춤형 스티커를 그리고 있습니다... (약 10~20초 소요)'):
                # 모델 리스트에서 사용 가능한 Imagen 모델 확인 후 호출
                # 보통 'imagen-3.0-generate-001' 모델명을 사용합니다.
                model = genai.GenerativeModel('gemini-1.5-flash') # 텍스트 보조용 (선택사항)
                
                # 이미지 생성 호출 (최신 SDK의 Imagen 호출 문법 반영)
                # 만약 imagen-3.0-generate-001 모델이 직접 호출되지 않는 경우를 대비해 
                # 공식 문서의 최신 메소드 형식을 따릅니다.
                
                # 이미지 생성 모델 객체 생성
                imagen = genai.get_model('models/imagen-3.0-generate-001')
                
                # 이미지 생성 실행
                result = imagen.generate_images(
                    prompt=image_prompt,
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="block_some",
                    person_generation="allow_adult"
                )
                
                if result and result.images:
                    st.success("짜잔! 스티커가 완성되었습니다.")
                    
                    # 스티커 카드 디자인
                    st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                        <h2 style="color: #FF4B4B; margin: 0;">🌟 참 잘했어요! 🌟</h2>
                        <p style="font-size: 1.2rem; color: #333; margin-top: 10px;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 생성된 이미지 표시
                    generated_image = result.images[0]
                    # 이미지가 PIL Image 객체이거나 바이트 데이터일 수 있음
                    st.image(generated_image._pil_image, use_column_width=True)
                    
                    # 다운로드 버튼 준비
                    buf = io.BytesIO()
                    generated_image._pil_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="스티커 다운로드하기",
                        data=byte_im,
                        file_name="praise_sticker.png",
                        mime="image/png"
                    )
                else:
                    st.error("이미지를 생성하지 못했습니다. Google AI Studio에서 Imagen 모델 접근 권한을 확인해 보세요.")
                    
        except Exception as e:
            # 구체적인 에러 메시지 출력
            st.error(f"오류가 발생했습니다: {str(e)}")
            if "404" in str(e):
                st.info("💡 힌트: Google AI Studio 사이트의 'Settings'에서 'Imagen' 기능이 활성화되어 있는지 확인해 보세요. 일부 지역이나 계정에서는 모델명이 다를 수 있습니다.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Imagen 3")

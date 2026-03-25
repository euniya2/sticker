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
            # API 설정
            genai.configure(api_key=api_key)
            
            # 칭찬 스티커용 프롬프트
            image_prompt = f"A cute and friendly 3D cartoon character sticker for a student who {praise_text}. White background, vibrant colors, sticker style with a thick white border, high quality, centered."
            
            with st.spinner('AI가 스티커를 그리고 있습니다... (약 10~20초 소요)'):
                # 최신 방식 (ImageGenerationModel) 시도
                # 계정에 따라 권한이 있는 모델이 다를 수 있으므로 순차적으로 시도합니다.
                candidate_models = [
                    'imagen-4.0-generate-001',        # Imagen 4
                    'imagen-3.1-flash-image-preview', # Nano Banana 2
                    'imagen-3.0-generate-001'         # Imagen 3
                ]
                
                result = None
                active_model = None
                
                # ImageGenerationModel 클래스 지원 여부 확인
                if hasattr(genai, 'ImageGenerationModel'):
                    for model_name in candidate_models:
                        try:
                            model = genai.ImageGenerationModel(model_name)
                            # 이미지 생성 시도
                            result = model.generate_images(
                                prompt=image_prompt,
                                number_of_images=1,
                                safety_filter_level="block_some",
                                person_generation="allow_adult"
                            )
                            if result and result.images:
                                active_model = model_name
                                break
                        except Exception:
                            continue
                    
                    if result and result.images:
                        st.success(f"스티커가 완성되었습니다! (사용 모델: {active_model})")
                        
                        # 스티커 카드 디자인 UI
                        st.markdown(f"""
                        <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                            <h2 style="color: #FF4B4B; margin: 0;">🌟 참 잘했어요! 🌟</h2>
                            <p style="font-size: 1.2rem; color: #333; margin-top: 10px;"><strong>"{praise_text}"</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        generated_image = result.images[0]
                        # PIL 이미지 추출 시도
                        if hasattr(generated_image, '_pil_image'):
                            display_img = generated_image._pil_image
                        else:
                            display_img = generated_image
                        
                        st.image(display_img, use_column_width=True)
                        
                        # 다운로드 버튼
                        buf = io.BytesIO()
                        display_img.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label="스티커 다운로드하기",
                            data=byte_im,
                            file_name="praise_sticker.png",
                            mime="image/png"
                        )
                    else:
                        st.error("이미지 생성 모델에 접근할 수 없거나 권한이 없습니다. Google AI Studio 설정을 확인해 주세요.")
                else:
                    st.error("설치된 라이브러리 버전이 낮아 이미지 생성 클래스를 찾을 수 없습니다. requirements.txt를 다시 확인해 주세요.")

        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            st.info("💡 힌트: API 키가 정확한지, 혹은 해당 모델 사용 권한이 있는지 확인이 필요합니다.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Imagen 최신 모델 대응")

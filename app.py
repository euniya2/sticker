import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pkg_resources

# 페이지 설정
st.set_page_config(page_title="AI 칭찬 스티커 생성기", layout="centered")

st.title("🎨 AI 맞춤형 칭찬 스티커 생성기")

# 현재 설치된 라이브러리 버전 확인 및 표시
try:
    current_version = pkg_resources.get_distribution("google-generativeai").version
    st.caption(f"현재 서버 SDK 버전: {current_version}")
except:
    current_version = "알 수 없음"
    st.caption("SDK 버전을 확인할 수 없습니다.")

st.write("학생의 잘한 점을 입력하면 AI가 귀여운 캐릭터 스티커를 만들어 줍니다!")

# 사이드바 설정 (API Key 입력)
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Google API Key를 입력하세요", type="password")
    st.info("Google AI Studio에서 발급받은 키를 입력해 주세요.")
    st.markdown("[API 키 발급받기](https://aistudio.google.com/app/apikey)")
    
    # 디버깅: 버전이 낮을 경우 경고
    if current_version != "알 수 없음" and current_version < "0.8.0":
        st.error(f"⚠️ 현재 버전({current_version})이 낮아 이미지 생성이 제한될 수 있습니다.")
        st.warning("GitHub의 requirements.txt를 'google-generativeai>=0.8.2'로 수정해 보세요.")

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
                # 1. 최신 방식 (ImageGenerationModel) 시도
                if hasattr(genai, 'ImageGenerationModel'):
                    # Jenius님의 스크린샷에 있던 최신 모델명 리스트 시도
                    # 순서대로 시도하여 작동하는 모델을 찾습니다.
                    candidate_models = [
                        'imagen-3.1-flash-image-preview', # Nano Banana 2
                        'imagen-4.0-generate-001',        # Imagen 4
                        'imagen-3.0-generate-001'         # Imagen 3
                    ]
                    
                    result = None
                    for model_name in candidate_models:
                        try:
                            model = genai.ImageGenerationModel(model_name)
                            result = model.generate_images(prompt=image_prompt, number_of_images=1)
                            if result and result.images:
                                break
                        except:
                            continue
                    
                    if result and result.images:
                        st.success(f"완성! (사용된 모델: {model_name})")
                        
                        # 스티커 카드 디자인 UI
                        st.markdown(f"""
                        <div style="background-color: white; padding: 20px; border-radius: 20px; border: 5px solid #FFD700; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;">
                            <h2 style="color: #FF4B4B; margin: 0;">🌟 참 잘했어요! 🌟</h2>
                            <p style="font-size: 1.2rem; color: #333; margin-top: 10px;"><strong>"{praise_text}"</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        generated_image = result.images[0]
                        # PIL 이미지 추출
                        display_img = generated_image._pil_image if hasattr(generated_image, '_pil_image') else generated_image
                        st.image(display_img, use_column_width=True)
                        
                        # 다운로드 버튼
                        buf = io.BytesIO()
                        display_img.save(buf, format="PNG")
                        st.download_button(label="스티커 다운로드하기", data=buf.getvalue(), file_name="praise_sticker.png", mime="image/png")
                    else:
                        st.error("이미지 생성 모델에 접근할 수 없습니다. 모델 권한을 확인해 주세요.")
                
                # 2. 구버전 또는 다른 방식 (fallback)
                else:
                    st.error(f"현재 SDK 버전({current_version})에서는 전용 이미지 생성 클래스를 지원하지 않습니다.")
                    st.info("💡 **최후의 방법:** GitHub의 requirements.txt 내용을 모두 지우고 아래 세 줄만 다시 입력한 뒤, 앱을 Delete 후 다시 Deploy 하세요.")
                    st.code("streamlit\ngoogle-generativeai==0.8.2\npillow")

        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            st.info("API 키가 올바른지, 혹은 Google AI Studio에서 Imagen 모델 사용 설정이 되어 있는지 확인해 주세요.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - Imagen 최신 버전 대응")

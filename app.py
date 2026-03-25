import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

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
                          help="칭찬 내용을 바탕으로 AI가 스티커 테마를 결정합니다.")

# 4. 생성 로직
if st.button("칭찬 스티커 만들기"):
    if not api_key:
        st.error("먼저 사이드바에 Google API Key를 입력해 주세요!")
    elif not praise_text:
        st.warning("칭찬 내용을 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 스티커 생성용 프롬프트 (교육용 컨셉)
            image_prompt = f"A cute, friendly 3D cartoon character sticker for a student who {praise_text}. White background, vibrant colors, clean sticker style with a thick white border, high resolution, centered composition."
            
            with st.spinner('내 계정의 최신 AI 모델을 찾아 연결 중입니다...'):
                # [중요] 내 계정에서 사용 가능한 이미지 생성 모델 목록 확인
                all_models = genai.list_models()
                image_models = [m.name for m in all_models if 'image' in m.name]
                
                if not image_models:
                    st.error("사용 가능한 이미지 생성 모델이 없습니다. API 권한을 확인하세요.")
                    st.stop()

                # 우선순위: Imagen 4 -> Imagen 3 -> Gemini Flash Image
                # Jenius님 계정에서 확인된 모델들 위주로 배정
                preferred_models = [
                    'models/imagen-4.0-generate-001',
                    'models/imagen-4.0-fast-generate-001',
                    'models/gemini-2.5-flash-image',
                    'models/imagen-3.0-generate-001'
                ]
                
                target_model = None
                for pm in preferred_models:
                    if pm in image_models:
                        target_model = pm
                        break
                
                if not target_model:
                    target_model = image_models[0] # 없으면 첫 번째 모델 사용

                st.caption(f"🚀 활성화된 모델: {target_model}")

                # [핵심 수정] 모델 호출 방식
                # ImageGenerationModel 클래스가 존재하면 사용, 아니면 GenerativeModel 사용
                if hasattr(genai, 'ImageGenerationModel'):
                    model = genai.ImageGenerationModel(target_model.replace('models/', ''))
                    response = model.generate_images(
                        prompt=image_prompt,
                        number_of_images=1
                    )
                    img_data = response.images[0]
                else:
                    # 라이브러리 버전이 낮을 경우를 대비한 대체 호출
                    model = genai.GenerativeModel(target_model)
                    response = model.generate_content(image_prompt)
                    # 모델에 따라 응답 구조가 다를 수 있음
                    img_data = response.candidates[0].content.parts[0].inline_data.data

                # 5. 결과 시각화
                if img_data:
                    st.success("교육용 칭찬 스티커가 완성되었습니다!")
                    
                    # 카드 스타일 UI
                    st.markdown(f"""
                    <div style="background-color: white; padding: 25px; border-radius: 20px; border: 4px dashed #FFD700; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px;">
                        <h2 style="color: #FF4B4B; margin: 0; font-family: 'Nanum Gothic';">✨ 참 잘했어요! ✨</h2>
                        <hr style="border: 0.5px solid #eee; margin: 15px 0;">
                        <p style="font-size: 1.3rem; color: #444; line-height: 1.6;"><strong>"{praise_text}"</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 이미지 표시
                    # PIL 이미지 객체인지 바이너리인지 확인 후 처리
                    if hasattr(img_data, '_pil_image'):
                        final_img = img_data._pil_image
                    elif isinstance(img_data, bytes):
                        final_img = Image.open(io.BytesIO(img_data))
                    else:
                        final_img = img_data
                        
                    st.image(final_img, use_column_width=True)
                    
                    # 다운로드 버튼
                    buf = io.BytesIO()
                    final_img.save(buf, format="PNG")
                    st.download_button(
                        label="💾 스티커 이미지 저장하기",
                        data=buf.getvalue(),
                        file_name="praise_sticker.png",
                        mime="image/png"
                    )

        except Exception as e:
            st.error(f"생성 중 오류 발생: {str(e)}")
            st.info("💡 팁: 'Reboot app'을 한 번 더 실행하거나, 잠시 후 다시 시도해 보세요.")

st.divider()
st.caption("Jenius의 바이브 코딩 실습 프로젝트 3 - AI 칭찬 스티커 생성기")

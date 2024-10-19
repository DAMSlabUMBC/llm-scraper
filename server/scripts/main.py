from setup import client
from scraping import scrape_website
from analysis.image_analysis import analyze_image_elements
from analysis.text_analysis import analyze_text_elements
from analysis.code_analysis import analyze_code_elements
from analysis.audio_analysis import analyze_audio_elements
from analysis.video_analysis import analyze_video_elements

def main():
    url = "https://www.amazon.com/All-New-release-Smart-speaker-Charcoal/dp/B09B8V1LZ3/ref=pd_ci_mcx_mh_mcx_views_0"
    text_content, video_content, image_content, audio_content, link_content, code_content = scrape_website(url)

    # text_result = analyze_text_elements(text_content)
    # video_result = analyze_video_elements(video_content)
    # image_result = analyze_image_elements(image_content)
    # audio_result = analyze_audio_elements(audio_content)
    # code_result = analyze_code_elements(code_content)

    # print(text_result)
    # print(video_result)
    # print(image_result)
    # print(audio_result)
    # print(code_result)

if __name__ == "__main__":
    main()
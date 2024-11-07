from setup import client
from scraping import scrape_website
from analysis.image_analysis import analyze_image_elements
from analysis.text_analysis import analyze_text_elements
from analysis.code_analysis import analyze_code_elements
from analysis.audio_analysis import analyze_audio_elements
from analysis.video_analysis import analyze_video_elements
from agents.model import response

def main():
    #url = 'https://web.dev/articles/video-and-source-tags'
    url = "https://www.amazon.com/Govee-Changing-Dynamic-Bluetooth-Assistant/dp/B09B7NQT2K/ref=shss_Detail_from_B09B8V1LZ3_f_LIGHTING_to_B09B7NQT2K/147-0083935-6529626?pd_rd_w=epnts&content-id=amzn1.sym.3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_p=3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_r=54TVWMKHD7550ZERRWVY&pd_rd_wg=aN3po&pd_rd_r=055b1d6f-291d-4e43-8fe5-125446bc8ab8&pd_rd_i=B09B7NQT2K&psc=1"
    # url = "https://www.target.com/p/bissell-little-green-hydrosteam-pet-3605/-/A-88682898#lnk=sametab"
    #url = "https://nowsecure.nl"
    #url = "https://www.walmart.com/ip/Nikon-D3500-DSLR-Camera-with-18-55mm-Lens-1590-Starter-Bundle/566604061?athAsset=eyJhdGhjcGlkIjoiNTY2NjA0MDYxIiwiYXRoc3RpZCI6IkNTMDIwIiwiYXRoYW5jaWQiOiJJdGVtQ2Fyb3VzZWwiLCJhdGhyayI6MC4wfQ%3D%3D&athena=true&sid=a494c519-54de-4fe5-a52a-edf6384f6d7d"
    text_content, image_content, code_content = scrape_website(url)

    text_result = analyze_text_elements(text_content)
    # video_result = analyze_video_elements(video_content)
    # image_result = analyze_image_elements(image_content)
    # audio_result = analyze_audio_elements(audio_content)
    # code_result = analyze_code_elements(code_content)

    print(text_result)
    # print(video_result)
    # print(image_result)
    # print(audio_result)
    # print(code_result)


    # This is the multi-agent workflow code

    # workflow = response()

    # initial_state = {
    #     "task": "Analyze scraped content",
    #     "text": "",
    #     "image": "",
    #     "content": [],  # Empty list to aggregate results
    #     "draft": "",
    #     "scraped_text": text_content,
    #     "scraped_images": "",
    # }


    # Run the workflow using stream and get the final state
    # final_state = None
    # for state in workflow.graph.stream(initial_state):
    #     final_state = state

    # print(final_state['generate']['draft'])

    # test.everything(url)

if __name__ == "__main__":
    main()
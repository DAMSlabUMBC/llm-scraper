import sys
sys.dont_write_bytecode = True
from setup import client
from scraping import scrape_website, preprocess, numTokens
from analysis.image_analysis import analyze_image_elements
from analysis.entity_analysis import analyze_text_elements
from analysis.relationship_analysis import generate, parse_string_to_list
from agents.model import response
from KG import createKG
from url_extraction.scrapping_manager import ScrappingManager

def test():
    #url = 'https://web.dev/articles/video-and-source-tags'
    # url = "https://www.amazon.com/Govee-Changing-Dynamic-Bluetooth-Assistant/dp/B09B7NQT2K/ref=shss_Detail_from_B09B8V1LZ3_f_LIGHTING_to_B09B7NQT2K/147-0083935-6529626?pd_rd_w=epnts&content-id=amzn1.sym.3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_p=3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_r=54TVWMKHD7550ZERRWVY&pd_rd_wg=aN3po&pd_rd_r=055b1d6f-291d-4e43-8fe5-125446bc8ab8&pd_rd_i=B09B7NQT2K&psc=1"
    #url = "https://www.target.com/p/bissell-little-green-hydrosteam-pet-3605/-/A-88682898#lnk=sametab"
    #url = "https://nowsecure.nl"
    #url = "https://www.walmart.com/ip/Nikon-D3500-DSLR-Camera-with-18-55mm-Lens-1590-Starter-Bundle/566604061?athAsset=eyJhdGhjcGlkIjoiNTY2NjA0MDYxIiwiYXRoc3RpZCI6IkNTMDIwIiwiYXRoYW5jaWQiOiJJdGVtQ2Fyb3VzZWwiLCJhdGhyayI6MC4wfQ%3D%3D&athena=true&sid=a494c519-54de-4fe5-a52a-edf6384f6d7d"
    url = "https://www.amazon.com/Apple-Smartwatch-Midnight-Aluminium-Detection/dp/B0DGJ736JM?crid=2Z5EADHK5OYT1&dib=eyJ2IjoiMSJ9.1cTuCkIwNQO-1bA68s81TE0Kz_WVqIeY_wElW53jwxLrmR5kPhUWTPkxQ5pCEMpfKnC3HvPO2PC7C6j2z8aCLkeEe8rbfGvrAx_VdUFJp8hoI9UqFR-snzWF0uOUc3X0mHzyk5uXLcD0qbg41iTSqcdu81Vv9ORhb3p7p6Il44WQpFyYlEm3VaEa8ccyh48xF3xF6LFTE2RMDA8217c7Dz_vROz5-5zVc_qHMF3sG9Y.zlZF_2ZiOH4tD-xRZlnHxECOB4JT2sKxLE8TY9oOSZ4&dib_tag=se&keywords=apple+watch&qid=1738798712&sprefix=apple+watch%2Caps%2C117&sr=8-3"
    text_content, image_content, code_content, video_content = scrape_website(url)
    
    text_result = analyze_text_elements(text_content)
    print("✅ Finish Text Result", text_result)
    video_result = analyze_text_elements(video_content)
    print("✅ Finish Video Result")
    code_result = analyze_text_elements(code_content)
    print("✅ Finish Code Result")
    image_result = analyze_image_elements(image_content)
    print("✅ Finish Image Result")


    print("\n=== Analysis Results ===")
    print("Text Analysis:", text_result)
    print("Code Analysis:", code_result)
    print("Video Analysis:", video_result)
    print("Image Analysis:", image_result)
    print("=====================\n")

    

    entities = f"""
        Text: {text_result}
        Video: {video_result}
        Image: {image_result}
        Code: {code_result}
    """
    print("Entities:",entities)
    generate_result = generate(entities)

    print('[😻] Final Response: ', generate_result)
      
if __name__ == "__main__":
    test()
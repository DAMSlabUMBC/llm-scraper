from setup import client
from scraping import scrape_website
from analysis.image_analysis import analyze_image_elements
from analysis.text_analysis import analyze_text_elements
from analysis.code_analysis import analyze_code_elements
from analysis.audio_analysis import analyze_audio_elements
from analysis.video_analysis import analyze_video_elements
from analysis.generate import generate, parse_string_to_list
from agents.model import response
from KG import createKG
from url_extraction.scrapping_manager import ScrappingManager
import logging
from tqdm import tqdm

logging.basicConfig(filename='scrapping.log', filemode="a", level=logging.INFO)

# all defined modules
AmazonModule = "Amazon"

def main():
    URL_list = []
    #triplets_list = []

    """# makes a new url extractor
    url_extractor = ScrappingManager()

    # initializes the modules the user wants to add to the url extractor
    url_extractor.initializeModule(AmazonModule)

    # fetches the urls of a module
    URL_set = url_extractor.getProductURLs(AmazonModule, "search_queries.txt")

    print(URL_set)


    URL_list = list(URL_set)[:5]"""
    
    with open("triplets3.txt", "w") as file:
        print("EMPTYING TRIPLETS FILE")
    
    with open("Amazon_product_urls.txt", "r") as file:
        URL_list = file.readlines()
        
    URL_list = URL_list[559:1000]

    #URL_list = ["https://www.amazon.com/Govee-Changing-Dynamic-Bluetooth-Assistant/dp/B09B7NQT2K/ref=shss_Detail_from_B09B8V1LZ3_f_LIGHTING_to_B09B7NQT2K/147-0083935-6529626?pd_rd_w=epnts&content-id=amzn1.sym.3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_p=3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_r=54TVWMKHD7550ZERRWVY&pd_rd_wg=aN3po&pd_rd_r=055b1d6f-291d-4e43-8fe5-125446bc8ab8&pd_rd_i=B09B7NQT2K&psc=1"]

    for url in tqdm(URL_list):
        #url = 'https://web.dev/articles/video-and-source-tags'
        #url = "https://www.amazon.com/Govee-Changing-Dynamic-Bluetooth-Assistant/dp/B09B7NQT2K/ref=shss_Detail_from_B09B8V1LZ3_f_LIGHTING_to_B09B7NQT2K/147-0083935-6529626?pd_rd_w=epnts&content-id=amzn1.sym.3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_p=3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_r=54TVWMKHD7550ZERRWVY&pd_rd_wg=aN3po&pd_rd_r=055b1d6f-291d-4e43-8fe5-125446bc8ab8&pd_rd_i=B09B7NQT2K&psc=1"
        #url = "https://www.target.com/p/bissell-little-green-hydrosteam-pet-3605/-/A-88682898#lnk=sametab"
        #url = "https://nowsecure.nl"
        #url = "https://www.walmart.com/ip/Nikon-D3500-DSLR-Camera-with-18-55mm-Lens-1590-Starter-Bundle/566604061?athAsset=eyJhdGhjcGlkIjoiNTY2NjA0MDYxIiwiYXRoc3RpZCI6IkNTMDIwIiwiYXRoYW5jaWQiOiJJdGVtQ2Fyb3VzZWwiLCJhdGhyayI6MC4wfQ%3D%3D&athena=true&sid=a494c519-54de-4fe5-a52a-edf6384f6d7d"
        try:
            text_content, image_content, code_content, video_content = scrape_website(url)

            if text_content == "" and image_content == "" and code_content == "" and video_content == "":
                exit()

            # preprocesses the text content
            text_content = preprocess(text_content)

            # writes the results of the preprocessed text in a text file
            with open("preprocessed_text.txt", "w", encoding="utf-8") as f:
                f.write(text_content)

            #print(f"num tokens {numTokens(text_content)}")


            #exit()

            text_content = " ".join(text_content.split("\n"))

            """with open("text_content.txt", "w", encoding="utf-8") as f:
                f.write(text_content)"""
            #print(text_content)

            text_result = analyze_text_elements(text_content)
            video_result = analyze_text_elements(video_content)
            code_result = analyze_text_elements(code_content)
            image_result = analyze_text_elements(analyze_image_elements(image_content))

            """print("\n=== Analysis Results ===")
            print("Text Analysis:", text_result)
            print("Code Analysis:", code_result)
            print("Video Analysis:", video_result)
            print("Image Analysis:", image_result)
            print("=====================\n")"""



            entities = f"""
                Text: {text_result}
                Video: {video_result}
                Image: {image_result}
                Code: {code_result}
            """
            #print("Entities:",entities)
            generate_result = generate(entities)

            #print('[😻] Final Response: ', generate_result)

            result_list = parse_string_to_list(generate_result)
            """print(type(result_list))
            print(result_list)"""

            triplets_list = []

            for triplet in result_list:
                triplets_list.append(str(triplet))

            with open("triplets3.txt", "a") as file:
                for triplet in triplets_list:
                    file.writelines(str(triplet))
                    file.write("\n")

            logging.info(f"finished extracting {url}")
        except:
            logging.error(f"error extracting {url}")
            
if __name__ == "__main__":
    main()
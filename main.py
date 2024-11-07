import scraping



def logo():
    print(r"                                                                             ")
    print(r"    /\_____/\       ███████╗███╗   ██╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗    ")
    print(r"   /  o   o  \      ██╔════╝████╗  ██║██╔═══██╗██╔═══██╗██║ ██╔╝╚██╗ ██╔╝    ")
    print(r"  ( ==  ^  == )     ███████╗██╔██╗ ██║██║   ██║██║   ██║█████╔╝  ╚████╔╝     ")
    print(r"   )         (      ╚════██║██║╚██╗██║██║   ██║██║   ██║██╔═██╗   ╚██╔╝      ")
    print(r"  (           )     ███████║██║ ╚████║╚██████╔╝╚██████╔╝██║  ██╗   ██║       ")
    print(r" ( (  )   (  ) )    ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ")
    print(r"(__(__)___(__)__)                The Curius Web Scraper v1.0                 ")
    print(r"                                                                             ")


def main():
    logo()
    url = "https://www.amazon.com/Govee-Changing-Dynamic-Bluetooth-Assistant/dp/B09B7NQT2K/ref=shss_Detail_from_B09B8V1LZ3_f_LIGHTING_to_B09B7NQT2K/147-0083935-6529626?pd_rd_w=epnts&content-id=amzn1.sym.3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_p=3965df22-b2a7-4de9-ac7b-82ff9bda5696&pf_rd_r=54TVWMKHD7550ZERRWVY&pd_rd_wg=aN3po&pd_rd_r=055b1d6f-291d-4e43-8fe5-125446bc8ab8&pd_rd_i=B09B7NQT2K&psc=1"
    #url = "https://www.target.com/p/bissell-little-green-hydrosteam-pet-3605/-/A-88682898#lnk=sametab"
    #url = "https://nowsecure.nl"
    #url = "https://www.walmart.com/ip/Nikon-D3500-DSLR-Camera-with-18-55mm-Lens-1590-Starter-Bundle/566604061?athAsset=eyJhdGhjcGlkIjoiNTY2NjA0MDYxIiwiYXRoc3RpZCI6IkNTMDIwIiwiYXRoYW5jaWQiOiJJdGVtQ2Fyb3VzZWwiLCJhdGhyayI6MC4wfQ%3D%3D&athena=true&sid=a494c519-54de-4fe5-a52a-edf6384f6d7d"
    scraping.everything(url)
    #scraping.walmart(url)
if __name__ == "__main__":
    main()
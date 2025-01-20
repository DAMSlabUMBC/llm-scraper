from url_extraction.modules.Amazon import Amazon
import os
from tqdm import tqdm
import urllib.parse

# defines all available modules
MODULES = {"Amazon": Amazon()}

class ScrappingManager():

    def __init__(self):
        self.modules = []
        self.directory = os.getcwd()
        

    def initializeModule(self, moduleName):
        """
        initializes a module to be added to the lab scraper

        Parameters:
        moduleName: name of the module
        """
        # checks if the lab scraper supports that module
        if moduleName in MODULES:
           
            # checks for duplicate modules
            if MODULES[moduleName] in self.modules:
               print(f"ERROR: Module {moduleName} already initialized in the Lab Scraper")
            else:

                # adds the module to the lab scraper
                self.modules.append(moduleName)
        else:
            print(f"ERROR: Lab Scraper doesn't support module {moduleName}")

    def getProductURLs(self, moduleName, search_queries_txt):
        """
        gets the product urls

        Parameters:
        search_queries_txt: path leading to the txt file with search queries
        moduleName: name of the module

        Return
        URL_set: a set of product urls
        """

        # checks if the lab scraper supports that module
        if moduleName in MODULES:

            # checks if the module is already instantiated in the lab scraper
            if moduleName in self.modules:

                # sets the current module
                module = MODULES[moduleName]

                # obtains the links to the search queries
                URL_queries = self.fetchSearchQueries(search_queries_txt, module.home)

                # obtain product urls by search query links
                URL_set = set(module.fetchURLs(URL_queries))

                # records the product urls of that module
                self.recordURLs(module, URL_set)

                return URL_set

            else:
                print(f"ERROR: Attempted to use {moduleName} Module before Initialize")
            
        else:
            print(f"ERROR: Lab Scraper doesn't support module {moduleName}")

    def fetchSearchQueries(self, path, home):
        """
        fetches URLS by parsing them from the website via search

        Parameters
        path: path to text file with a list of categories to search
        home: module's home url

        Return
        search_urls: list of urls for parsing products from
        """
        search_urls = []
        # open the category file to be read
        with open(path, 'r') as f:

            # interates through each category to be searched
            for category in f:

                # enters the category to be searched
                category = category.rstrip()
                encoded_query = urllib.parse.quote(category)

                # adds search url to the list
                search_url = home + encoded_query
                search_urls.append(search_url)

        f.close()

        return search_urls
    
    def recordURLs(self, module, URL_set):

        products_txt = module.name + "_product_urls.txt"

        with open(products_txt, "w") as f:
            for url in URL_set:
                f.writelines(url)
                f.write("\n")

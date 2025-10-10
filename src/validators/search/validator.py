"""Main triple validation orchestration."""

from src.types.triple import Triple
from .search import SearchClient
from .format import QueryFormatter
from .corrupt import TripleCorruptor


class TripleValidator:
    """Main validator that orchestrates the validation process."""
    
    def __init__(self, headless: bool = False):
        self.search_client = SearchClient(headless=headless)
        self.query_formatter = QueryFormatter()
        self.corruptor = TripleCorruptor(self.query_formatter)
    
    def validate(
        self, 
        triple: Triple, 
    ) -> bool:
        """Validate a triple by comparing search results with corrupted variants."""


        # Step 1: Search the triple and paraphrases
        normal_queries = self.query_formatter.format_triple(triple)
        print(f"Searching {len(normal_queries)} normal variants...")
        print(f"Normal Queries: ", normal_queries)
        normal_res = self.search_client.search_queries(normal_queries)
        print(f"Normal results: {normal_res}")

        # Early page gate: are any variants showing lots of pages?
        max_normal_pages = max((r.pages for r in normal_res), default= 0)
        if max_normal_pages > 1:
            print(f"Strong evidence (pages> 1), skipping corruption check")
            return True # Thought: We can return a weight based off the pages: 2 pages = 0.2, 4 pages = 0.4, etc.
        
        print(f"Weak evidence (pages < 1), performing the corruption check")

        # Step 2: The page check was inconclusive, create corrupted triples
        corrupt_queries = self.corruptor.generate_corrupted_queries(triple)
        print(f"Searching {len(corrupt_queries)} corrupted variants...")
        print(f"Corrupt Queries: ", corrupt_queries)
        corrupt_res = self.search_client.search_queries(corrupt_queries)
        print(f"Corrupted results: {corrupt_res}")

        # Compare the search results from the original and corrupted triple
        max_normal_results = max((r.results for r in normal_res), default=0)
        max_corrupt_results = max((r.results for r in corrupt_res), default=0)
        if max_normal_results > max_corrupt_results:
            # Conclusive, our original query had more search results than our corrupted
            print(f"Strong evidence (normal results > corrupted results), skipping other validation methods")
            return True # Create a weight formula 

        # Inconclusive, we move to the next validation method
        return False

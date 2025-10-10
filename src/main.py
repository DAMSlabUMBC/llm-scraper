from src.validators.search import Triple, TripleNode, TripleValidator

def main():
    triple = Triple(
        subject=TripleNode("device", "Nest Thermostat"),
        predicate="manufacturedBy",
        object=TripleNode("manufacturer", "Google")
    )
    
    validator = TripleValidator(headless=False)
    is_valid = validator.validate(triple)
    
    print(f"\nTriple is {'VALID' if is_valid else 'INVALID'}")


if __name__ =="__main__":
    main()
import ast
import glob
from itertools import combinations
import concurrent.futures

def read_file(filepath):
    """Read the file and return structured data."""
    structured_data = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    parsed_tuple = ast.literal_eval(line)
                    structured_data.add(parsed_tuple)
                except (SyntaxError, ValueError, TypeError):
                    print(f"🤯 Skipping invalid line in {filepath}: {line}")
    return structured_data

def compare_two_files(file1, file2):
    """Comparing the files"""
    content1 = read_file(file1)
    content2 = read_file(file2)

    missing_2 = content1 - content2 # content1 - content2
    missing_2_percentage = (len(missing_2) / len(content1) * 100) if content1 else 0 # calculated by (missing / total)

    return {
        "file1": file1,
        "file2": file2,
        "missing_2": missing_2,
        "missing_2_percentage": round(missing_2_percentage, 2),
    }

def main():
    # Automatically find all .txt files in the directory
    txt_files = sorted(glob.glob("*.txt"))

    if not txt_files:
        print("No .txt files found in the folder!")
        return

    all_content = set()
    comparisons = []
    
    # Thread to make it faster >:)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        thread_comparison = {executor.submit(compare_two_files, file1, file2): (file1, file2) for file1, file2 in combinations(txt_files, 2)}
        
        for compare in concurrent.futures.as_completed(thread_comparison):
            try:
                result = compare.result()
                comparisons.append(result)
                all_content.update(read_file(result["file1"]))
                all_content.update(read_file(result["file2"]))
                all_content.update(result["missing_2"])
            except Exception as e:
                print(f"⚠️ Error comparing {thread_comparison[compare]}: {e}")
                
    # Iterate and compare files
    for file1, file2 in combinations(txt_files, 2):
        result = compare_two_files(file1, file2)
        comparisons.append(result)

        # Combine all data
        all_content.update(read_file(file1))
        all_content.update(read_file(file2))
        all_content.update(result["missing_2"])
        
    combined_file = "combined.txt"
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("\n".join(str(item) for item in sorted(all_content)))  # Write structured data

    for result in comparisons:
        print(f"\nComparing {result['file1']} -> {result['file2']}")
        #print(f"Missing from {result['file2']}: {result['missing_from_2']}")
        print(f"Missing Percentage: {result['missing_2_percentage']}%")
        
    
    
    total_percentage = sum(res["missing_2_percentage"] for res in comparisons) / len(comparisons)
    print(f"\nTotal Missing Percentage: {total_percentage}%")
    print(f"✅ All structured data merged into {combined_file}!")

if __name__ == "__main__":
    main()

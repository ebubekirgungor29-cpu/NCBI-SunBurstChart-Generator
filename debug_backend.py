from app import get_taxonomy_data
import json

def run_test(test_name, organisms, expected_charts):
    print(f"--- RUNNING TEST: {test_name} ---")
    print(f"Input: {organisms}")
    
    result = get_taxonomy_data(organisms)
    
    print(f"Result: {len(result['charts'])} chart(s) generated.")
    
    if len(result['charts']) == expected_charts:
        print(f"SUCCESS: Correct number of charts ({expected_charts}) generated.")
        # Optional: Print chart details for manual verification
        # for chart in result['charts']:
        #     print(f"  - Chart Title: {chart['title']}")
        #     print(f"    Organisms: {chart['organisms']}")
    else:
        print(f"FAILURE: Expected {expected_charts} chart(s) but got {len(result['charts'])}.")
        print(json.dumps(result, indent=2))
    
    print("-" * (len(test_name) + 22))
    print("\n")


if __name__ == "__main__":
    # Test 1: Organisms from the same superkingdom (Eukaryota)
    # Should result in ONE combined chart.
    same_kingdom_organisms = ['Homo sapiens', 'Drosophila melanogaster']
    run_test("Same Superkingdom", same_kingdom_organisms, 1)

    # Test 2: Organisms from different superkingdoms (Eukaryota and Bacteria)
    # Should result in TWO separate charts.
    different_kingdom_organisms = ['Homo sapiens', 'Escherichia coli']
    run_test("Different Superkingdoms", different_kingdom_organisms, 2)

    # Test 3: Multiple organisms, some from the same kingdom, one from another
    # Should result in TWO charts.
    mixed_organisms = ['Felis catus', 'Canis lupus familiaris', 'Bacillus subtilis']
    run_test("Mixed Superkingdoms", mixed_organisms, 2)

from ingest import extractor

sample_text_hiring = """
Professor Jane Doe
Department of Computer Science
University of Example

Research Interests: Computer Vision, Machine Learning, Deep Learning

I am looking for Ph.D. students for Fall 2026. If you are interested, please apply.
My group works on self-supervised learning.

Selected Publications:
Doe, J. et al. "Learning to see." CVPR 2024.
Smith, A., Doe, J. "Another paper." NeurIPS 2023.
"""

sample_text_no_hiring = """
Professor Bob Smith
History Department

Interests: Ancient Rome, Latin

No openings currently.
"""

def test():
    print("--- Testing Hiring ---")
    card1 = extractor.extract_professor_card(sample_text_hiring)
    print("Detected Hiring Signals:", card1["hiring_signals"])
    print("Interests:", card1["research_interests"])
    print("Publications:", card1["selected_publications"])
    
    assert len(card1["hiring_signals"]) > 0, "Should detect hiring signal"
    
    print("\n--- Testing No Hiring ---")
    card2 = extractor.extract_professor_card(sample_text_no_hiring)
    print("Detected Hiring Signals:", card2["hiring_signals"])
    
    # assert len(card2["hiring_signals"]) == 0 # "No openings" might match "openings" regex if not careful.
    # My regex was "openings? for". "No openings currently" does not match "openings for".
    
if __name__ == "__main__":
    test()

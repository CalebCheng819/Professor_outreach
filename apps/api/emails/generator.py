from typing import Dict, Any

TEMPLATES = {
    "summer_intern": {
        "subject": "Inquiry regarding Summer Internship opportunities - {name}",
        "body": """Dear Professor {lastname},

I hope this email finds you well.

My name is [My Name], and I am a [Year] student at [My University] majoring in [Major]. I have been following your work on {interest_1} and {interest_2}, and I am very interested in your research group.

I was particularly fascinated by your recent work on [Mention a Paper if possible], and I would love to contribute to similar projects.

I am writing to inquire if there are any openings for summer research internships in your lab. I have attached my CV and transcript for your review.

Thank you for your time and consideration.

Sincerely,
[My Name]
[My Website/Portfolio]"""
    },
    "phd_inquiry": {
        "subject": "Prospective Ph.D. Student Fall 202X - {name}",
        "body": """Dear Professor {lastname},

I am writing to express my strong interest in pursuing a Ph.D. under your supervision at {affiliation}, starting in Fall 202X.

I am currently a student at [My University], where I have been working on [My Research Topic]. I successfully [Achievement].

Your research in {interest_1} aligns perfectly with my academic interests. I am specifically drawn to your work on {interest_2}.

I would appreciate the opportunity to discuss your research and potential Ph.D. opportunities in your lab.

Best regards,
[My Name]"""
    }
}

def generate_email(professor: Any, card_data: Dict[str, Any], template_type: str = "summer_intern") -> Dict[str, str]:
    if template_type not in TEMPLATES:
        template_type = "summer_intern"
    
    template = TEMPLATES[template_type]
    
    # helper for names
    parts = professor.name.split()
    lastname = parts[-1] if parts else "Professor"
    
    # helper for interests
    interests = card_data.get("research_interests", [])
    i1 = interests[0] if len(interests) > 0 else "your research area"
    i2 = interests[1] if len(interests) > 1 else "related topics"
    
    context = {
        "name": professor.name,
        "lastname": lastname,
        "affiliation": professor.affiliation,
        "interest_1": i1,
        "interest_2": i2
    }
    
    return {
        "subject": template["subject"].format(**context),
        "body": template["body"].format(**context)
    }

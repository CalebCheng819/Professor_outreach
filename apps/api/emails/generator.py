from typing import Dict, Any

TEMPLATES = {
    # --- Summer Intern Templates ---
    "summer_intern": {
        "subject": "Inquiry regarding Summer Research Internship - {name}",
        "body": """Dear Professor {lastname},

I hope you are doing well.

My name is [My Name], and I am a [Year] student at [My University] majoring in [Major]. I have been following your work on {interest_1}, and I am very interested in your research group.

I was particularly fascinated by your recent work on [Mention a Paper], and I would love to contribute to similar projects.

I am writing to inquire if there are any openings for summer research internships in your lab. I have attached my CV and transcript for your review.

Sincerely,
[My Name]
[My Website]"""
    },
    
    # --- PhD Templates ---
    "phd": {
        "subject": "Prospective Ph.D. Student Fall 202X - {name}",
        "body": """Dear Professor {lastname},

I am writing to express my strong interest in pursuing a Ph.D. under your supervision at {affiliation}, starting in Fall 202X.

I am currently a student at [My University], where I have been working on [My Research Topic].

Your research in {interest_1} aligns perfectly with my academic interests. I am specifically drawn to your work on {interest_2}.

I would appreciate the opportunity to discuss your research and potential Ph.D. opportunities in your lab.

Best regards,
[My Name]
[My Website]"""
    },

    # --- Postdoc Templates ---
    "postdoc": {
        "subject": "Postdoctoral Position Inquiry - {name}",
        "body": """Dear Professor {lastname},

I am writing to inquire about potential postdoctoral opportunities in your lab.

I recently completed my Ph.D. at [University] under the supervision of [Advisor], where my research focused on [Topic].

I have valid interest in your work on {interest_1} and believe my background in [Skill/Topic] would be a strong addition to your group.

Attached is my CV and a brief research statement. I would welcome the chance to discuss how I could contribute to your lab.

Best regards,
[My Name]"""
    },

    # --- RA Templates ---
    "ra": {
        "subject": "Inquiry regarding Research Assistant position - {name}",
        "body": """Dear Professor {lastname},

I am writing to express my interest in joining your lab as a Research Assistant.

I have a background in [Major/Field] and have experience with [Skill 1] and [Skill 2]. I am very interested in your work on {interest_1}.

Are you currently looking for RAs? I would love to discuss how I can contribute to your ongoing projects.

Best,
[My Name]"""
    }
}

def generate_email(professor: Any, card_data: Dict[str, Any], template_type: str = "standard") -> Dict[str, str]:
    # Determine the target role from the professor object, default to summer_intern
    role = getattr(professor, "target_role", "summer_intern") or "summer_intern"
    
    # Map generic template requests to role-specific logic if needed
    # For now, we simply use the role as the primary template key
    # If the user requested a specific style (e.g. 'research_focus'), we could append it, e.g. f"{role}_{style}"
    
    # Current simple logic: Always use the role-based template
    target_template = role
    
    if target_template not in TEMPLATES:
        target_template = "summer_intern"
    
    template = TEMPLATES[target_template]
    
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

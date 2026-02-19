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

def generate_email(professor: Any, card_data: Dict[str, Any], request: Any = None) -> Dict[str, str]:
    """
    Generates an email draft using LLM if available, otherwise falls back to templates.
    """
    from services.llm import LLMService

    llm = LLMService()
    
    # Extract request parameters
    template_type = "summer_intern"
    tone = "formal"
    length = "medium"
    custom_instructions = ""
    
    if request:
        template_type = getattr(request, "template", template_type)
        tone = getattr(request, "tone", tone)
        length = getattr(request, "length", length)
        custom_instructions = getattr(request, "custom_instructions", "")

    # Role override if not specified in request but exists on professor
    if not request or not getattr(request, "template", None):
         template_type = getattr(professor, "target_role", "summer_intern") or "summer_intern"

    # 1. Try LLM Generation
    if llm.enabled:
        try:
            return _generate_with_llm(llm, professor, card_data, template_type, tone, length, custom_instructions)
        except Exception as e:
            print(f"[Email Generator] LLM failed, falling back to template: {e}")

    # 2. Fallback to Static Templates
    target_template = template_type if template_type in TEMPLATES else "summer_intern"
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

def _generate_with_llm(llm, professor, card_data, template_type, tone, length, custom_instructions):
    import json
    
    # Prepare Context
    parts = professor.name.split()
    lastname = parts[-1] if parts else "Professor"
    
    summary = card_data.get("summary", "No summary available.")
    interests = ", ".join(card_data.get("research_interests", []))
    
    # Build Prompt
    system_prompt = f"""You are an expert academic assistant helping a student write an email to a professor.
    Role: Student writing to Professor {lastname} at {professor.affiliation}.
    Goal: Write a {tone} email for a {template_type.replace('_', ' ')} position.
    Length: {length} (keep it concise but impactful).
    
    Professor's Research Context:
    - Interests: {interests}
    - Summary: {summary}
    
    {f'Custom Instructions: {custom_instructions}' if custom_instructions else ''}
    
    Output strictly valid JSON with keys: "subject" and "body"."""
    
    user_prompt = f"Draft the email to Professor {professor.name}."
    
    # Call LLM (using the internal _call_ollama method for direct prompt control or parse_search_results style)
    # Since LLMService doesn't have a generic "chat" method exposed publicly yet, 
    # we might need to use its internal _call_ollama or add a new method.
    # For now, let's look at how `parse_search_results` calls `_call_ollama`.
    # It uses `_call_ollama` which takes a single prompt string.
    # We will construct a single prompt string that includes system instructions.
    
    # Remove the manual prompt concatenation since we now support system prompts
    # full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nResponse (JSON):"
    
    # Debug Logs
    print(f"[Email Generator] System Prompt:\n{system_prompt}")
    print(f"[Email Generator] User Prompt:\n{user_prompt}")

    # Call LLM with separate system prompt
    try:
        response_text = llm.chat(user_prompt, system_prompt=system_prompt)
    except Exception as e:
        print(f"[Email Generator] LLM Call Failed: {e}")
        raise e

    print(f"[Email Generator] Raw Response:\n{response_text}")
    
    # Parse JSON
    try:
        # Clean up code blocks if LLM adds them
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
             response_text = response_text.split("```")[1].split("```")[0]
             
        data = json.loads(response_text)
        return {
            "subject": data.get("subject", "Inquiry"),
            "body": data.get("body", "Error generating body.")
        }
    except Exception as e:
        print(f"[Email Generator] JSON Parse Failed: {e}. Text was: {response_text}")
        raise ValueError(f"Failed to parse LLM JSON: {e}")

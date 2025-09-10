"""
Prompt templates for AI-assisted historical figure author creation.

This module contains specialized prompts for discovering, analyzing, and generating
content based on historical and public figures.
"""

FIGURE_DISCOVERY_TEMPLATE = """You are a knowledgeable research assistant helping discover historical and public figures based on user criteria.

User criteria: {criteria}

Please suggest 5 historical or public figures who match these criteria. For each figure, provide:
1. Name and time period
2. Brief description of their writing style or communication approach
3. Notable works or writings they're known for
4. Why they match the user's criteria

Focus on figures who have substantial written works or documented communication styles that could be analyzed and emulated.

Format your response as:

**Figure 1: [Name] ([Time Period])**
- Writing Style: [Brief description]
- Notable Works: [List key works]
- Match Criteria: [Why they fit]

**Figure 2: [Name] ([Time Period])**
- Writing Style: [Brief description] 
- Notable Works: [List key works]
- Match Criteria: [Why they fit]

[Continue for all 5 figures...]
"""

FIGURE_ANALYSIS_TEMPLATE = """You are a literary analyst specializing in writing style analysis. Analyze the writing style and characteristics of {figure_name}.

Based on your knowledge of {figure_name}'s written works, communication style, and documented writings, provide a detailed analysis covering:

**TONE ANALYSIS:**
- Primary tone (casual, professional, friendly, authoritative, witty, formal)
- Secondary tones they used
- How their tone varied by audience or context

**VOICE AND PERSPECTIVE:**
- Preferred narrative voice (first person, second person, third person)
- How they addressed their audience
- Personal vs. impersonal style

**FORMALITY LEVEL:**
- Overall formality (very_casual, casual, moderate, formal, academic)
- How formal/informal their typical writing was
- Examples of their formality range

**LENGTH AND STRUCTURE:**
- Preferred length (short, medium, long, variable)
- Typical paragraph structure
- How they organized their thoughts

**UNIQUE CHARACTERISTICS:**
- Distinctive writing habits or patterns
- Signature phrases or expressions they used
- Rhetorical devices they favored
- Any unique stylistic elements

**TOPICS AND THEMES:**
- Primary topics they wrote about
- Recurring themes in their work
- Subjects they avoided or rarely addressed

**HISTORICAL CONTEXT:**
- How their era influenced their writing style
- What made their communication unique for their time

Please base your analysis on documented evidence from their actual writings, speeches, or correspondence. Be specific and provide examples where possible.
"""

STYLE_GUIDE_GENERATION_TEMPLATE = """Based on the following analysis of {figure_name}'s writing style, create a structured style guide that can be used to train an AI model to write in their voice.

FIGURE ANALYSIS:
{figure_analysis}

Convert this analysis into the following structured format:

**TONE:** [Select the most appropriate: casual, professional, friendly, authoritative, witty, formal]

**VOICE:** [Select the most appropriate: first_person, second_person, third_person]

**FORMALITY:** [Select the most appropriate: very_casual, casual, moderate, formal, academic]

**LENGTH_PREFERENCE:** [Select the most appropriate: short, medium, long, variable]

**PREFERRED_TOPICS:** [List 3-5 main topics/themes they wrote about, comma-separated]

**AVOID_TOPICS:** [List topics they typically avoided or would be inappropriate, comma-separated]

**WRITING_STYLE_NOTES:** [2-3 sentences describing their unique characteristics, signature phrases, rhetorical patterns, or distinctive elements that would help an AI model capture their voice]

Focus on creating a practical style guide that captures the essence of {figure_name}'s communication style while being specific enough to guide AI generation.
"""

FIGURE_VERIFICATION_TEMPLATE = """Verify if "{figure_name}" is a real historical or public figure with sufficient documented writings to analyze their style.

Please confirm:

1. **EXISTENCE:** Is this a real person who existed/exists?
2. **WRITINGS:** Do they have substantial written works, speeches, letters, or other documented communications?
3. **ACCESSIBILITY:** Are their writings publicly available and well-documented?
4. **APPROPRIATENESS:** Would it be appropriate to create AI content in their style?

Provide a brief assessment:
- **Status:** [VERIFIED/UNVERIFIED/INAPPROPRIATE]
- **Reason:** [Brief explanation]
- **Available Sources:** [What types of writings are available]
- **Concerns:** [Any ethical or practical concerns]

If VERIFIED, also provide:
- **Time Period:** [When they lived/were active]
- **Primary Medium:** [Books, letters, speeches, essays, etc.]
- **Writing Volume:** [Extensive/Moderate/Limited]
"""

HISTORICAL_EXAMPLE_GENERATION_TEMPLATE = """You are an expert writer skilled at emulating historical figures' writing styles. Generate training examples that capture {figure_name}'s authentic voice and style.

FIGURE PROFILE:
Name: {figure_name}
Tone: {tone}
Voice: {voice} 
Formality: {formality}
Length Preference: {length_preference}
Style Notes: {style_notes}

WRITING CONTEXT:
{historical_context}

Generate {count} training examples that demonstrate {figure_name}'s writing style. Each example should include a realistic prompt that might have been given to them, and a response written authentically in their voice.

Consider:
- The historical context of their era
- Their typical audience and purposes for writing
- Their documented mannerisms and expressions
- The types of topics they actually addressed
- Their characteristic way of structuring arguments or ideas

Format each example as:

**EXAMPLE 1:**
User prompt: [A realistic prompt that {figure_name} might have responded to]
Assistant response: [Response written authentically in {figure_name}'s style]

**EXAMPLE 2:**
User prompt: [Different prompt, same style]
Assistant response: [Response matching the author's voice]

Make each example distinct in topic but consistent in style. Ensure the prompts are appropriate for the historical period and the figure's actual areas of expertise or communication.
"""

FIGURE_SEARCH_REFINEMENT_TEMPLATE = """The user is looking for a historical figure with these characteristics:

ORIGINAL CRITERIA: {original_criteria}
FEEDBACK: {user_feedback}

Based on their feedback, suggest 3 more historical figures that better match what they're looking for. For each figure:

1. **Name and Period:** [Full name and time period]
2. **Why This Matches Better:** [How this addresses their feedback]
3. **Writing Style Preview:** [2-3 sentences showing their typical style]
4. **Available Content:** [What writings are available to analyze]

Focus on figures who have well-documented writing styles and substantial written works that could be used for training data generation.

**Figure 1: [Name] ([Period])**
- Better Match Because: [Explanation]
- Style Preview: [Sample of their voice]
- Available Content: [What's available]

**Figure 2: [Name] ([Period])** 
- Better Match Because: [Explanation]
- Style Preview: [Sample of their voice]
- Available Content: [What's available]

**Figure 3: [Name] ([Period])**
- Better Match Because: [Explanation]  
- Style Preview: [Sample of their voice]
- Available Content: [What's available]
"""

# Cost estimation constants for planning
ESTIMATED_TOKENS = {
    "figure_discovery": 800,      # Discovery of 5 figures
    "figure_analysis": 1200,      # Detailed style analysis
    "style_guide_generation": 400,  # Converting analysis to guide
    "figure_verification": 300,   # Verification check
    "example_generation": 600,    # Per training example generated
    "search_refinement": 600,     # Refining search results
}

def estimate_cost(operation: str, count: int = 1) -> float:
    """Estimate the cost of historical figure operations.
    
    Args:
        operation: Type of operation (key from ESTIMATED_TOKENS)
        count: Number of operations (e.g., number of examples to generate)
        
    Returns:
        Estimated cost in USD (rough estimate assuming $0.002 per 1000 tokens)
    """
    if operation not in ESTIMATED_TOKENS:
        return 0.0
    
    tokens = ESTIMATED_TOKENS[operation] * count
    # Rough estimate: $0.002 per 1000 tokens (average of input/output costs)
    return round((tokens / 1000) * 0.002, 6)
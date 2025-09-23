"""
Prompt templates for AI-assisted historical figure author creation.

This module contains specialized prompts for discovering, analyzing, and generating
content based on historical and public figures.
"""

FIGURE_DISCOVERY_TEMPLATE = """You are a knowledgeable research assistant helping discover historical and public figures based on user criteria.

User criteria: {criteria}

Please suggest {count} historical or public figures who match these criteria. For each figure, provide:
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

[Continue for all {count} figures...]
"""

FIGURE_NAME_SEARCH_TEMPLATE = """You are a knowledgeable research assistant helping find specific historical figures based on their names.

The user is looking for: {name_query}

Please find up to {count} historical or public figures whose names match or are similar to "{name_query}". Consider:
- Exact name matches
- Alternative spellings or variations
- Similar sounding names
- Pen names or aliases
- Figures commonly known by similar names

For each matching figure, provide:
1. Full name (and aliases if applicable)
2. Time period and basic biographical info
3. Brief description of their writing style or communication approach
4. Notable works or writings they're known for
5. Why they match the search (exact match, similar name, etc.)

Focus on figures who have substantial written works or documented communication styles that could be analyzed.

If you cannot find any figures matching "{name_query}", suggest the closest matches you can think of and explain why no exact matches were found.

Format your response as:

**Figure 1: [Full Name] ([Time Period])**
- Also Known As: [Aliases/pen names if any]
- Writing Style: [Brief description]
- Notable Works: [List key works]
- Match Type: [Exact match/Similar spelling/Alias/etc.]

**Figure 2: [Full Name] ([Time Period])**
- Also Known As: [Aliases/pen names if any]
- Writing Style: [Brief description]
- Notable Works: [List key works]
- Match Type: [Exact match/Similar spelling/Alias/etc.]

[Continue for all matching figures found, up to {count}...]

If no matches found, explain why and suggest alternative search terms or similar figures.
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

If VERIFIED, also provide detailed corpus assessment:
- **Time Period:** [When they lived/were active]
- **Primary Medium:** [Books, letters, speeches, essays, etc.]
- **Writing Volume:** [Extensive/Moderate/Limited]
- **Corpus Richness:** [Rich/Moderate/Sparse - based on variety and volume of available works]
- **Famous Works:** [List 3-5 of their most well-known works if applicable]
- **Notable Quotes:** [Are they known for memorable quotations? Yes/No]
- **Public Domain Status:** [Are their major works in public domain? Yes/No/Mixed/Unknown]
- **Best Source Works:** [Which specific works would be best for style analysis?]
- **Recommended Dataset Mode:** [Corpus-Heavy/Hybrid/Traditional - based on available material richness]

For figures with extensive written works (novels, essays, speeches), prioritize actual excerpts over generated examples.
For figures with rich quotable content, include famous quotes with proper context.
For figures with limited documented works, rely more on traditional AI-generated examples.
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

IMPORTANT: Aim for responses of varying lengths to teach the model flexibility:
- Target 800-1200 words for some responses (detailed essays or analyses)
- Target ~1500-2500 words for a few responses when context allows (comprehensive treatises or stories)
- If nearing token/context limits, prioritize coherent completion over length and truncate gracefully
- Include both shorter and longer examples to show the author's range
- Focus on substantial, well-developed content that showcases their full writing style

Consider:
- The historical context of their era
- Their typical audience and purposes for writing
- Their documented mannerisms and expressions
- The types of topics they actually addressed
- Their characteristic way of structuring arguments or ideas
- How they developed complex thoughts over longer passages

Format each example as:

**EXAMPLE 1:**
User prompt: [A realistic prompt that {figure_name} might have responded to]
Assistant response: [Comprehensive response of 1000-2000+ words written authentically in {figure_name}'s style]

**EXAMPLE 2:**
User prompt: [Different prompt requesting detailed analysis or extended writing]
Assistant response: [Substantial response matching the author's voice and demonstrating their ability to write at length]

Make each example distinct in topic but consistent in style. Ensure the prompts are appropriate for the historical period and the figure's actual areas of expertise. Create responses that show how the author would develop ideas fully and comprehensively.
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

ACTUAL_CONTENT_EXTRACTION_TEMPLATE = """You are a literary analyst helping to select the best excerpts from {figure_name}'s actual written works for training data.

Based on the figure's corpus assessment:
- Famous Works: {famous_works}
- Best Source Works: {best_source_works}
- Writing Style Characteristics: {style_characteristics}

Identify specific excerpts that would be ideal for training data. For each recommended excerpt, provide:

1. **Source Work:** [Title of the work]
2. **Excerpt Location:** [Chapter/Section/Page reference if known]
3. **Excerpt Length:** [Approximate word count: Short (200-500), Medium (500-1000), Long (1000-2500)]
4. **Style Showcase:** [What specific writing characteristics this excerpt demonstrates]
5. **Training Value:** [Why this excerpt would be valuable for style learning]
6. **Content Type:** [Dialogue, narrative, descriptive, argumentative, etc.]

Focus on excerpts that:
- Showcase the author's distinctive voice and style
- Represent different types of writing (dialogue, description, analysis)
- Are substantial enough to demonstrate full development of ideas
- Are from well-known works that define the author's reputation
- Display signature techniques, phrases, or rhetorical patterns

Recommend 8-12 specific excerpts that would create a comprehensive style training set.

Format as:
**EXCERPT 1: [Work Title]**
- Location: [Chapter/Section]
- Length: [Word count category]
- Style Showcase: [What it demonstrates]
- Training Value: [Why it's valuable]
- Content Type: [Type of writing]

**EXCERPT 2: [Work Title]**
[Continue for all recommendations...]

Prioritize excerpts that would be in the public domain and readily available.
"""

QUOTE_COLLECTION_TEMPLATE = """You are a literary researcher collecting famous quotes from {figure_name} for training data inclusion.

Based on the figure's profile:
- Notable for memorable quotations: {has_notable_quotes}
- Writing characteristics: {style_characteristics}
- Primary themes: {primary_themes}

Identify 15-25 of their most famous, well-documented quotes that showcase their:
- Distinctive voice and personality
- Core beliefs and philosophies
- Characteristic way of expressing ideas
- Memorable turns of phrase
- Intellectual or creative insights

For each quote, provide:

1. **Quote Text:** [The exact quotation]
2. **Source/Context:** [Where it's from - work, speech, letter, interview, etc.]
3. **Theme/Topic:** [What the quote is about]
4. **Style Element:** [What writing characteristic it demonstrates]
5. **Training Prompt:** [A realistic prompt that could have elicited this response]

Focus on quotes that are:
- Definitively attributed to the author
- Representative of their thinking and expression
- Varied in topic and tone
- Substantial enough to show their voice (avoid very short phrases)
- Suitable for training an AI to capture their communication style

Format as:
**QUOTE 1:**
- Text: "[Full quotation]"
- Source: [Origin/context]
- Theme: [Subject matter]
- Style Element: [What it showcases]
- Training Prompt: [Prompt that might generate this response]

**QUOTE 2:**
[Continue for all quotes...]

Ensure quotes span different topics and showcase the range of their expression.
"""

PROMPT_FOR_EXCERPT_TEMPLATE = """You are creating realistic training prompts for actual excerpts from {figure_name}'s written works.

For the following actual excerpt from their work:

SOURCE: {source_work}
EXCERPT: {excerpt_text}
CONTEXT: {excerpt_context}

Create 2-3 different prompts that could realistically have generated this response from {figure_name}. The prompts should:

1. Be appropriate for the historical period and the author's typical audience
2. Match the content and tone of the excerpt
3. Reflect the types of requests or questions the author might have encountered
4. Be specific enough to generate the provided response
5. Vary in approach (analytical request, creative prompt, direct question, etc.)

Consider:
- The author's area of expertise and interests
- The style and content of the excerpt
- The historical context and typical writing purposes
- The audience the author typically addressed

Format as:
**PROMPT OPTION 1:** [First prompt possibility]
**PROMPT OPTION 2:** [Second prompt possibility]
**PROMPT OPTION 3:** [Third prompt possibility]

Each prompt should be 1-3 sentences and feel natural for someone to have asked {figure_name}.
"""

# Cost estimation constants for planning
ESTIMATED_TOKENS = {
    "figure_discovery": 200,  # Base cost per figure in discovery (scaled by count)
    "figure_name_search": 150,  # Base cost per figure in name search (scaled by count)
    "figure_analysis": 1500,  # Detailed style analysis
    "style_guide_generation": 400,  # Converting analysis to guide
    "figure_verification": 400,  # Enhanced verification check with corpus assessment
    "example_generation": 2000,  # Per training example generated (increased for longer examples)
    "search_refinement": 800,  # Refining search results
    "content_extraction": 1200,  # Identifying best excerpts from actual works
    "quote_collection": 1000,  # Collecting and contextualizing famous quotes
    "prompt_for_excerpt": 300,  # Generating prompts for actual excerpts (per excerpt)
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
        available_operations = ", ".join(ESTIMATED_TOKENS.keys())
        raise ValueError(
            f"Unknown operation '{operation}'. Available operations: {available_operations}"
        )

    tokens = ESTIMATED_TOKENS[operation] * count
    # Rough estimate: $0.005 per 1000 tokens (average of input/output costs)
    return round((tokens / 1000) * 0.005, 6)

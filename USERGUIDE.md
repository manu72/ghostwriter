# Ghostwriter Stage 1 POC - User Guide

This guide will help you test the core functionality of Ghostwriter's Stage 1 Proof of Concept. You can create a personal AI author that writes in your style through a simple 4-step process, or use AI to create authors based on historical figures.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **OpenAI API key** (required for fine-tuning)
3. **Terminal/Command line** access

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace 'your_openai_api_key_here' with your actual API key
```

Your `.env` file should look like:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_ORG_ID=your_openai_org_id_here_optional
```

## Testing the Complete Workflow

### Step 1: Create Your First Author

You have two options for creating authors:

#### Option A: Manual Author Creation (Original Method)

Start with the init command for a guided setup:

```bash
python -m cli.main init
```

This will walk you through creating an author profile with:

- Author name and description
- Writing style preferences (tone, voice, formality)
- Topics you write about
- Style notes

**Alternative**: Create an author directly:

```bash
python -m cli.main author create my_author --name "My Author" --description "Test author"
```

#### Option B: Historical Figure Author Creation (NEW!)

Create an AI author based on a historical figure's writing style:

```bash
python -m cli.main historical create
```

This AI-assisted process will:

1. **Discover Historical Figures** - Search for figures matching your criteria
2. **Analyze Writing Style** - AI analyzes the figure's documented writing characteristics  
3. **Generate Author Profile** - Automatically creates style guide based on analysis
4. **Create Training Dataset** - AI generates training examples in the figure's style
5. **Ready for Training** - Seamlessly integrates with existing training workflow

**Example workflow:**
```bash
# Interactive discovery and creation
python -m cli.main historical create

# Direct figure specification  
python -m cli.main historical create --figure "Mark Twain" --id twain_author

# Search for figures with enhanced options
python -m cli.main historical search "famous American authors"           # Auto-detected as description
python -m cli.main historical search "Virginia Woolf"                   # Auto-detected as name
python -m cli.main historical search "poets" --count 15                 # Get more results
python -m cli.main historical search "Hemingway" --mode name --count 10 # Explicit name mode

# Analyze a specific figure's style (includes verification check with override option)
python -m cli.main historical analyze "Virginia Woolf"
```

**Benefits of Historical Authors:**
- No need to manually define writing style - AI does the analysis
- Automatically generates training examples matching the figure's voice
- Creates diverse, high-quality datasets based on documented writing patterns
- Perfect for exploring different writing styles or emulating admired authors

**Cost:** AI analysis and dataset generation typically costs $0.10-0.30 total per historical author.

#### 🆕 Corpus-Based Dataset Generation

For well-documented historical figures (like Hemingway, Jane Austen, Shakespeare, etc.), Ghostwriter now automatically incorporates actual content from their works:

**How It Works:**
1. **Corpus Assessment**: AI evaluates the figure's available written works, famous quotes, and public domain content
2. **Dataset Mode Selection**: Automatically chooses optimal generation strategy:
   - **Corpus-Heavy Mode**: Authors with extensive documented works (novels, essays, speeches)
   - **Hybrid Mode**: Authors with moderate documentation (mix of actual + AI content)
   - **Traditional Mode**: Authors with limited documented works (AI-generated only)
3. **Content Integration**: For corpus-rich authors, datasets include:
   - Actual famous quotes with appropriate prompts
   - References to excerpts from their most celebrated works
   - AI-generated examples that complement the actual content

**Examples of Each Mode:**

```bash
# Corpus-Heavy Mode Authors (Rich Documentation)
python -m cli.main historical create --figure "Ernest Hemingway"
# → Incorporates actual quotes from "The Sun Also Rises", "A Farewell to Arms"
# → References his distinctive prose style from famous passages
# → AI generates additional examples matching his voice

python -m cli.main historical create --figure "Jane Austen"
# → Includes her witty social commentary quotes
# → References excerpts from "Pride and Prejudice", "Emma"
# → Shows her characteristic irony and dialogue style

python -m cli.main historical create --figure "William Shakespeare"
# → Famous quotes from plays and sonnets
# → References to soliloquies and memorable passages
# → AI examples in Elizabethan style

# Hybrid Mode Authors (Moderate Documentation)
python -m cli.main historical create --figure "Maya Angelou"
# → Select famous quotes and AI-generated examples
# → Balanced approach for comprehensive style coverage

# Traditional Mode Authors (Limited Documentation)
python -m cli.main historical create --figure "Lesser Known Historical Writer"
# → AI-generated examples based on available style analysis
# → Still authentic to documented characteristics
```

**Benefits:**
- **Higher Authenticity**: Real quotes and excerpts provide genuine voice samples
- **Better Training Quality**: Actual content teaches the model authentic patterns
- **Comprehensive Coverage**: Combines real content with AI examples for full style representation
- **Automatic Selection**: System chooses the best approach based on available material
- **Cost Efficient**: Leverages existing high-quality content rather than generating everything

**Production Note**: The current implementation simulates excerpt integration. A production system would connect to public domain text databases to include actual chapter-length excerpts from authors' works.

#### Historical Figure Verification & User Override

The AI system automatically verifies historical figures before proceeding with analysis and dataset generation. Here's how it works:

**Verification Process:**
1. **Smart Verification**: AI analyzes the figure's authenticity, available sources, and documentation quality
2. **🆕 Corpus Assessment**: For verified figures, evaluates corpus richness, famous works, quote availability, and public domain status
3. **Dataset Mode Recommendation**: Suggests optimal generation approach based on available content
4. **Detailed Report**: Shows verification status (VERIFIED/UNVERIFIED), reasoning, available sources, and concerns
5. **User Override Option**: For unverified figures, you can choose to proceed after clear warnings

**Example Verification Flow:**

**For Unverified Figure:**
```bash
$ python -m cli.main historical analyze "Fictional Character"

✅ Verifying figure: Fictional Character...

❌ Verification: UNVERIFIED

Reason: Not a documented historical figure
Available Sources: Limited or fictional content only
Concerns: May result in inconsistent training data

⚠️  Warning: Figure 'Fictional Character' is not verified
Reason: Not a documented historical figure
Concerns: May result in inconsistent training data

Proceeding with unverified figures may result in:
• Lower quality training data
• Inaccurate style analysis
• Poor model performance

Are you sure you want to proceed with this unverified figure? [y/N]:
```

**🆕 For Verified Figure with Corpus Assessment:**
```bash
$ python -m cli.main historical analyze "Ernest Hemingway"

✅ Verifying figure: Ernest Hemingway...

✅ Verification: VERIFIED

Reason: Well-documented American novelist and journalist
Available Sources: Extensive written works, letters, interviews
Time Period: 1899-1961
Primary Medium: Novels, short stories, journalism
Writing Volume: Extensive
Corpus Richness: Rich
Famous Works: "The Sun Also Rises", "A Farewell to Arms", "For Whom the Bell Tolls", "The Old Man and the Sea"
Notable Quotes: Yes
Public Domain Status: Mixed (some works in public domain)
Best Source Works: "The Sun Also Rises", "A Farewell to Arms", short stories
Recommended Dataset Mode: Corpus-Heavy

📊 Dataset mode: Corpus-Heavy
→ Will incorporate actual quotes and excerpts from famous works
→ Enhanced training quality with authentic content
```

**When to Use Override:**
- ✅ **Obscure but real figures**: Lesser-known historical figures the AI might not recognize
- ✅ **Recent public figures**: Contemporary writers, journalists, or public figures
- ✅ **Regional figures**: Historically significant people from specific regions or cultures
- ❌ **Fictional characters**: Generally not recommended for authentic style modeling
- ❌ **Composite personas**: Made-up figures combining traits from multiple people

**Best Practice:** Always review the verification details carefully. The AI provides reasoning for its decision, which helps you make an informed choice about whether to proceed.

#### Enhanced Historical Figure Search

The historical figure search system now includes powerful features for finding exactly the authors you need:

**Search Modes:**
- **Auto Mode (default)**: Intelligently detects whether your query is a name or description
- **Name Mode**: Searches specifically for figures matching the provided name
- **Description Mode**: Searches for figures matching descriptive criteria

**Smart Auto-Detection Examples:**
```bash
# These are automatically detected as NAME searches:
python -m cli.main historical search "Mark Twain"
python -m cli.main historical search "Dr. Martin Luther King"
python -m cli.main historical search "Sir Arthur Conan Doyle"

# These are automatically detected as DESCRIPTION searches:
python -m cli.main historical search "famous American authors"
python -m cli.main historical search "Victorian era poets"
python -m cli.main historical search "influential philosophers"
```

**Advanced Search Options:**
```bash
# Get more results (1-20, default is 5)
python -m cli.main historical search "poets" --count 15

# Force specific search mode
python -m cli.main historical search "Shakespeare" --mode name
python -m cli.main historical search "Hemingway" --mode description

# Combine options for precise control
python -m cli.main historical search "British writers" --mode description --count 20
```

**Smart Fallback System:**
When a name search finds no results, the system offers to automatically try a description search:
```
No figures found with name 'Unknown Author'
Try searching by description instead? [Y/n]: y
Falling back to description search...
```

**Search Tips:**
- **Use name mode** when you know exactly who you're looking for
- **Use description mode** for broad discovery of figures matching criteria
- **Increase count** if initial results don't include who you're seeking
- **Let auto-detection work** - it's accurate in most cases
- **Name searches cost less** than description searches (more targeted)

### Step 2: Build a Training Dataset

#### For Manual Authors (Option A)

Create training examples that represent your writing style:

```bash
python -m cli.main dataset build my_author
```

This opens an interactive menu where you can:

1. **Add examples from writing samples** - Paste your existing writing and get AI-suggested prompts
2. **Generate examples from prompts** - Create prompt/response pairs
3. **Import from text file** - Upload a text file to extract examples with AI prompt assistance
4. **Review current dataset** - See what examples you have so far
5. **Generate more examples from existing examples** - Use AI to create additional examples based on your existing ones (requires OpenAI API)

**Minimum recommendation**: Add 10-20 examples for basic fine-tuning.

#### For Historical Authors (Option B)

**Great news!** If you created a historical author, your training dataset was automatically generated during the creation process. The AI:

- Generated 10-50 training examples in the historical figure's authentic style
- Created appropriate prompts that the figure might have responded to
- Ensured historical accuracy and style consistency
- Allowed you to review and approve each example

**Need More Examples?** Historical authors have a specialized command for generating additional examples:

```bash
# Generate 10 more examples (default)
python -m cli.main historical build your_historical_author_id

# Generate specific number of examples
python -m cli.main historical build your_historical_author_id --count 20
```

This command:
- Re-analyzes the historical figure's writing style
- Generates high-quality examples in their authentic voice  
- Uses the same bulk accept feature as creation (accept all at once or review individually)
- Maintains historical accuracy and style consistency
- Automatically saves the expanded dataset

**Alternative:** You can also use the standard dataset building process:

```bash
python -m cli.main dataset build your_historical_author_id
```

#### AI-Assisted Prompt Creation

When adding examples from writing samples or importing from files, Ghostwriter offers two ways to create prompts:

**Option 1: Write your own prompt (free)**
- Manually create a prompt that would generate your writing sample
- Full control over prompt wording and specificity

**Option 2: Get AI-suggested prompt (~$0.001)**  
- AI analyzes your writing sample and suggests an appropriate prompt
- Shows cost estimate before making API calls
- You can accept, edit, or reject the AI suggestion
- Automatically falls back to manual entry if AI fails

**Example workflow:**
```
You provide: "Working from home requires discipline. Set up a dedicated workspace, 
establish boundaries, and use productivity tools to stay focused."

AI suggests: "Write practical tips for maintaining productivity while working from home"

You can: Accept, edit to "Write 3-5 practical tips for remote work productivity", or write manually
```

### Step 2.5: Generate More Examples with AI (Optional)

Once you have at least 2 or 3 examples, you can use AI to generate additional examples that match your writing style:

```bash
# Select option 5 in the dataset builder menu
# This feature will:
# - Analyse your first 3 existing examples
# - Generate 1-20 new examples using OpenAI API
# - Let you review, edit, or skip each generated example
# - Add approved examples to your dataset
```

**Benefits:**

- Quickly expand your dataset from a few seed examples
- Maintains consistency with your established writing style
- Reduces manual work while ensuring quality

**Cost:** Approximately $0.002-0.01 per generated example (OpenAI API charges apply)

**Benefits of AI-Assisted Prompts:**
- Reduces cognitive load when creating training examples
- Generates more effective prompts than manual writing
- Speeds up dataset building, especially for bulk text imports
- Provides educational value - learn from AI-suggested prompts
- Optional feature - manual entry always available

### Step 3: Validate Your Dataset

Check if your dataset is ready for fine-tuning:

```bash
python -m cli.main dataset validate my_author
```

This checks:

- Dataset size (warns if < 10 examples)
- Format correctness
- Content quality
- Diversity of examples
- Safety concerns

### Step 4: Fine-tune the Model

Start the fine-tuning process:

```bash
python -m cli.main train start my_author
```

**Note**: This requires a valid OpenAI API key and will incur costs (~$8-12 for a small dataset).

Options:

- `--wait` - Wait for training to complete (20+ minutes)
- `--model gpt-4o-mini` - Specify base model (default)

#### Quick Test Generation

Test your model immediately after training completes:

```bash
# Generate test content during training workflow
python -m cli.main train generate my_author --prompt "Write a test paragraph"
```

This is useful for quick validation that your model is working correctly.

### Step 5: Generate Content

Once training is complete, you have several options for generating content with your fine-tuned model:

#### Single Text Generation

Generate a single piece of content with a specific prompt:

```bash
# Single generation with prompt
python -m cli.main generate text my_author --prompt "Write about productivity"

# Interactive prompt entry
python -m cli.main generate text my_author
```

Options:
- `--max-completion-tokens 500` - Control response length
- `--save/--no-save` - Enable/disable saving generated content to files (default: enabled)

#### Interactive Generation Session

For multiple generations in a session without conversation memory:

```bash
python -m cli.main generate interactive my_author
```

This opens an interactive session where you can:
- Enter multiple prompts one after another
- Each generation is independent (no conversation memory)
- Type 'quit', 'exit', or 'q' to end the session
- Generated content is automatically saved to files

#### Chat Sessions (Conversation Mode)

**NEW!** Have full ChatGPT-style conversations with your fine-tuned model:

```bash
# Start new chat session
python -m cli.main generate chat my_author

# Resume existing session
python -m cli.main generate chat my_author --session <session_id>

# Disable auto-save (not recommended)
python -m cli.main generate chat my_author --no-save
```

**Chat Features:**
- **Conversation Memory**: Your model remembers the entire conversation context
- **Session Persistence**: Chat sessions are automatically saved and can be resumed
- **Rich Interface**: Beautiful formatting with timestamps and clear message distinction
- **Auto-Save**: All conversations are automatically saved unless disabled

**Chat Commands:**
During a chat session, use these commands:

- `/help` - Show available commands
- `/clear` - Clear conversation history (start fresh)
- `/history` - Show full conversation history
- `/save` - Manually save current session
- `/export` - Export chat as formatted markdown file
- `/info` - Show session information (ID, message count, timestamps)
- `/sessions` - List available saved sessions
- `/quit` or `/exit` - End chat session

**Example Chat Session:**
```
💬 Chat Session
Author: My Author
Session: abc123...
Messages: 0

💬 Type your message to chat, or use /help for commands.

💬 Hello! Can you help me write a blog post about remote work?

🤖 My Author: Of course! I'd be happy to help you write a blog post about remote work. 
Let me start with an engaging introduction and outline some key points...

💬 Great! Can you make it more focused on productivity tips?

🤖 My Author: Absolutely! Let me refine that to focus specifically on productivity 
strategies for remote workers...
```

**Benefits of Chat Mode:**
- **Context Awareness**: Model remembers what you've discussed
- **Iterative Refinement**: Ask for changes, improvements, or different approaches
- **Natural Conversation**: More like working with a human writing partner
- **Session Management**: Pick up conversations where you left off

## Monitoring and Management

### Check Overall Status

```bash
python -m cli.main status
```

Shows all authors, dataset sizes, and training status. Historical authors are marked with 🏛️ while manual authors show 👤.

### View Author Details

```bash
python -m cli.main author show my_author
```

### Check Training Progress

```bash
python -m cli.main train status my_author
```

### View Dataset Information

```bash
python -m cli.main dataset show my_author
```

### Dataset Management

Additional dataset commands:

```bash
# Export dataset to JSONL file
python -m cli.main dataset export my_author --output my_dataset.jsonl

# Clear all training examples (be careful!)
python -m cli.main dataset clear my_author
```

### Training Job Management

List and manage training jobs:

```bash
# List all training jobs for an author
python -m cli.main train list my_author

# Test a specific model quickly
python -m cli.main train test my_author
```

### Generated Content & Session Storage

**Content Storage:**
All generated content is automatically saved to your author's directory:
- `data/authors/<author_id>/content/` - Generated text files
- `data/authors/<author_id>/chats/` - Chat session files
- Files are named with timestamps for easy organization

**Chat Session Management:**
Chat sessions are persistent and stored locally:
- Sessions auto-save during conversation
- Resume any session using its ID
- Export conversations to markdown format
- Sessions include full conversation history and metadata

## Testing Scenarios

### Scenario 1: Complete Happy Path (Manual Author)

1. Run `init` and create author with guided setup
2. Build dataset with 5-10 examples using different input methods
3. Use AI generation (option 5) to expand to 15+ examples
4. Validate dataset (should show "READY" or "ACCEPTABLE")
5. Start training and wait for completion
6. Generate content with various prompts
7. Verify generated content matches author's style

### Scenario 1b: Historical Author Happy Path (NEW!)

1. Run `python -m cli.main historical create`
2. Search for historical figures with criteria like "famous American authors"
3. Select a figure from the AI-suggested list (e.g., Mark Twain)
4. Review AI analysis of the figure's writing style
5. Approve or customize the generated author profile
6. Review and approve AI-generated training examples (15-30 examples)
7. Start training immediately (dataset already complete)
8. Generate content and verify it matches the historical figure's style

### Scenario 2: Error Handling

1. Try commands without setting up API key (should show clear error)
2. Try to train with insufficient dataset (< 10 examples)
3. Try to generate content without a trained model
4. Test with invalid author names

### Scenario 3: AI-Assisted Prompt Creation

1. Create author and select "Add examples from writing samples" (option 1)
2. Paste a writing sample and choose "Get AI-suggested prompt" (option 2)
3. Test all three AI response options: accept, edit, reject
4. Try with different writing styles (formal, casual, technical)
5. Test API error handling by temporarily using invalid API key
6. Import text file and test AI prompts for multiple sections
7. Compare AI-suggested prompts vs manual prompts for quality

### Scenario 4: AI Generation Feature

1. Create author and add 3-5 examples manually
2. Use AI generation (option 5) to create 5-10 additional examples
3. Test review process: accept some, edit some, skip some
4. Verify generated examples maintain style consistency
5. Test with insufficient examples (< 2) to see error handling

### Scenario 5: Dataset Management

1. Create multiple authors with different styles
2. Test dataset import from text files
3. Clear and rebuild datasets
4. Export datasets to JSONL format
5. Test AI generation with different types of existing examples

### Scenario 6: Historical Figure Discovery (NEW!)

1. Test figure discovery with different criteria:
   - "famous poets"
   - "20th century scientists who wrote"
   - "influential philosophers"
   - "American Civil War era writers"
2. Use search refinement when initial results aren't suitable
3. Test figure verification with both valid and invalid figures:
   - Valid figures (should show VERIFIED status)
   - Invalid/fictional figures (should show UNVERIFIED with override option)
   - Test user override: decline and accept for unverified figures
4. **🆕 Test corpus assessment for verified figures:**
   - Rich corpus figures (Hemingway, Austen, Shakespeare) - should show Corpus-Heavy mode
   - Moderate corpus figures (Maya Angelou, contemporary authors) - should show Hybrid mode
   - Sparse corpus figures (lesser-known historical writers) - should show Traditional mode
   - Compare corpus richness assessments across different authors
5. Test enhanced search functionality:
   - Auto-detection with clear names vs. descriptions
   - Different count values (5, 10, 15, 20)
   - Explicit mode selection (name, description, auto)
   - Fallback from failed name search to description search
   - Search refinement with feedback
6. Compare AI analysis quality across different historical periods
7. Test figure analysis for figures with different writing mediums (books, letters, speeches)
8. Create multiple historical authors from different eras and compare styles

### Scenario 7: Enhanced Historical Figure Search Testing (NEW!)

1. Test smart auto-detection accuracy:
   ```bash
   # These should be detected as NAME searches:
   python -m cli.main historical search "Virginia Woolf"
   python -m cli.main historical search "Dr. Martin Luther King"
   python -m cli.main historical search "Sir Arthur Conan Doyle"

   # These should be detected as DESCRIPTION searches:
   python -m cli.main historical search "famous American poets"
   python -m cli.main historical search "Victorian era writers"
   python -m cli.main historical search "influential 20th century philosophers"
   ```

2. Test configurable result counts:
   ```bash
   python -m cli.main historical search "poets" --count 3    # Small result set
   python -m cli.main historical search "poets" --count 10   # Medium result set
   python -m cli.main historical search "poets" --count 20   # Large result set
   ```

3. Test explicit mode selection:
   ```bash
   # Force name mode (should find specific author)
   python -m cli.main historical search "Shakespeare" --mode name

   # Force description mode (should find related figures)
   python -m cli.main historical search "Shakespeare" --mode description

   # Compare results between modes for same query
   ```

4. Test smart fallback system:
   ```bash
   # Search for non-existent or misspelled name (should offer fallback)
   python -m cli.main historical search "Shakespear" --mode name
   # Accept fallback when prompted: y

   # Test declining fallback
   python -m cli.main historical search "Unknown Writer" --mode name
   # Decline fallback when prompted: n
   ```

5. Test edge cases and validation:
   ```bash
   # Invalid count (should show error)
   python -m cli.main historical search "test" --count 25

   # Invalid mode (should show error)
   python -m cli.main historical search "test" --mode invalid
   ```

6. Performance and cost testing:
   - Compare cost estimates between name and description searches
   - Test search speed with different count values
   - Verify cost scaling works correctly

### Scenario 8: Historical Author Dataset Building (NEW!)

1. Create a historical author with initial dataset
2. Test `historical build` with default count (10 examples)
3. Test with custom count: `--count 20`
4. Test bulk accept feature (accept all without review)
5. Test individual review process (accept some, edit some, skip some)
6. Verify dataset consistency between initial and additional examples
7. Compare quality of AI-generated examples across different historical figures

### Scenario 9: Corpus-Based Dataset Generation Testing (NEW!)

1. **Test Corpus-Heavy Mode Authors:**
   ```bash
   # Create authors known for extensive written works
   python -m cli.main historical create --figure "Ernest Hemingway"
   python -m cli.main historical create --figure "Jane Austen"
   python -m cli.main historical create --figure "Charles Dickens"
   ```
   - Verify "Corpus-Heavy" mode is automatically selected
   - Check that datasets include actual quotes with contextual prompts
   - Verify excerpt references from famous works are included
   - Compare dataset quality with traditional AI-only generation

2. **Test Hybrid Mode Authors:**
   ```bash
   # Create authors with moderate documentation
   python -m cli.main historical create --figure "Maya Angelou"
   python -m cli.main historical create --figure "Langston Hughes"
   ```
   - Verify "Hybrid" mode is selected
   - Check mix of actual quotes and AI-generated examples
   - Ensure balanced approach maintains authenticity

3. **Test Traditional Mode Fallback:**
   ```bash
   # Create lesser-known historical writers
   python -m cli.main historical create --figure "Lesser Known Historical Writer"
   ```
   - Verify fallback to "Traditional" mode for sparse corpus
   - Ensure AI-generated examples still capture documented style characteristics

4. **Compare Dataset Quality Across Modes:**
   - Create authors from each mode category
   - Compare training example authenticity and style consistency
   - Test fine-tuned models from each mode for style accuracy
   - Verify cost differences between modes

5. **Test Corpus Assessment Accuracy:**
   - Test with authors known to have rich documentation (should get Corpus-Heavy)
   - Test with authors having limited works (should get Traditional)
   - Verify public domain status assessment affects content selection
   - Check famous works and best source works identification accuracy

### Scenario 10: Chat Conversation Testing (NEW!)

1. Start new chat session and test basic conversation
2. Test conversation memory (model remembers previous messages)
3. Test all chat commands:
   - `/clear` - Clear conversation history
   - `/history` - Show conversation history
   - `/save` - Manual save
   - `/export` - Export to markdown
   - `/info` - Session information
   - `/sessions` - List available sessions
4. Test session resumption (exit and resume same conversation)
5. Test multiple concurrent sessions with different authors
6. Test long conversations (20+ message exchanges)
7. Export chat sessions and verify markdown format

## Expected Behavior

### ✅ Success Indicators

- Author creation completes without errors
- Dataset building saves examples correctly
- Validation shows "READY FOR FINE-TUNING" or "ACCEPTABLE WITH CAUTION"
- Training starts and completes successfully
- Generated content reflects the author's style

### ⚠️ Known Limitations (Stage 1 POC)

- Only supports OpenAI fine-tuning (gpt-3.5-turbo)
- No feedback/improvement loop yet
- Limited to local file storage
- Basic safety checks only
- No web UI (CLI only)

## Troubleshooting

### Common Issues

**"OpenAI API key not found"**

- Check that `.env` file exists and contains valid API key
- Ensure `.env` is in the project root directory

**"No fine-tuned model found"**

- Complete training first with `train start`
- Check training status with `train status`

**"Dataset validation failed"**

- Add more examples (minimum 10 recommended)
- Check example format in dataset review

**"Permission denied" or directory errors**

- Ensure write permissions in project directory
- Try running from project root

**Chat session issues**

**"Chat session not found"**
- Check session ID spelling/case
- Use `/sessions` command to list available sessions
- Start new session if needed

**Chat commands not working**
- Ensure commands start with `/` (e.g., `/help` not `help`)
- Type `/help` to see all available commands

**Generated content not saving**
- Check disk space in project directory
- Verify write permissions in `data/authors/<id>/` directory
- Use `--save` flag explicitly if needed

**Historical author build failing**

**"Could not verify figure" or "Figure verification failed"**
- Historical figure name may be ambiguous - try more specific name (e.g., "Mark Twain" instead of "Twain")
- Use `historical analyze <name>` first to test verification
- **NEW**: If figure shows as UNVERIFIED, you can choose to proceed with override:
  - Review the verification details and reasoning carefully
  - Consider if this is a lesser-known but real historical figure
  - Accept the override prompt if you're confident the figure is legitimate
  - Expect potentially lower quality results with unverified figures

**"Not a historical author"**
- Use `historical build` only for historical authors (created with `historical create`)
- Use `dataset build` for manually created authors

**Enhanced search issues**

**"No figures found matching your search"**
- Try increasing the count: `--count 15` or `--count 20`
- If using name mode, try description mode or let auto-detection decide
- Check spelling of figure names
- Try broader or more specific search terms

**"Auto-detected search mode: [mode]" seems wrong**
- Use explicit mode selection: `--mode name` or `--mode description`
- For ambiguous queries, the system defaults to description mode for safety
- Example: `"Shakespeare style"` → detected as description (use `--mode name` for the person)

**Search results don't include expected figure**
- Try different search terms or synonyms
- Increase result count: `--count 15` or `--count 20`
- Use name search for specific people: `--mode name`
- Check if the figure might be known by different names or titles

**"Invalid count" or "Invalid mode" errors**
- Count must be between 1-20
- Valid modes: auto, name, description
- Check command spelling and syntax

### Getting Help

**View command help:**

```bash
python -m cli.main --help
python -m cli.main author --help
python -m cli.main historical --help
python -m cli.main dataset --help
python -m cli.main train --help
python -m cli.main generate --help
```

**Complete Command Reference:**

**Author Management:**
- `author create <id>` - Create new author profile
- `author list` - List all authors
- `author show <id>` - Show author details
- `author edit <id>` - Edit author profile

**Historical Figures:**
- `historical create` - Create author from historical figure
- `historical search <query> [OPTIONS]` - Search for historical figures
  - `--count, -c INTEGER` - Number of results to return (1-20, default: 5)
  - `--mode, -m TEXT` - Search mode: auto, description, name (default: auto)
  - `--refine` - Refine previous search results
- `historical analyze <name>` - Analyze figure's writing style
- `historical build <id>` - Generate more examples for historical author

**Dataset Management:**
- `dataset build <id>` - Build training dataset interactively
- `dataset show <id>` - Show dataset information
- `dataset validate <id>` - Validate dataset quality
- `dataset export <id>` - Export dataset to JSONL
- `dataset clear <id>` - Clear all examples

**Training:**
- `train start <id>` - Start fine-tuning
- `train status <id>` - Check training progress
- `train list <id>` - List training jobs
- `train test <id>` - Quick model test
- `train generate <id>` - Generate test content

**Content Generation:**
- `generate text <id>` - Single text generation
- `generate interactive <id>` - Interactive generation session
- `generate chat <id>` - Start chat conversation

**System:**
- `init` - Initialize and create first author
- `status` - Show overview of all authors
- `version` - Show version information

**Check logs:** Look for error messages in terminal output - they provide specific guidance.

## Cost Expectations

Fine-tuning costs with OpenAI (as of 2024):

- Small dataset (10-50 examples): ~$3-8
- Medium dataset (50-100 examples): ~$8-15
- Token costs for generation: ~$0.01-0.02 per 1000 tokens

**AI-assisted features:**
- AI-suggested prompts: ~$0.001 per prompt suggestion
- AI-generated examples: ~$0.002-0.01 per generated example
- Historical figure analysis & dataset generation: ~$0.10-0.30 per complete historical author
- Historical author dataset building: ~$0.05-0.15 per 10 additional examples
- Chat conversations: ~$0.01-0.05 per message exchange (depending on conversation length)
- All AI features show cost estimates before making API calls

## Success Criteria

The Stage 1 POC is working correctly if:

1. ✅ You can create an author profile in under 5 minutes
2. ✅ Dataset building is intuitive and supports multiple input methods
3. ✅ Historical author creation works end-to-end with AI analysis and generation
4. ✅ **🆕 Corpus-based generation automatically incorporates actual quotes and excerpts for well-documented authors**
5. ✅ **🆕 Dataset mode selection accurately reflects the author's available written corpus**
6. ✅ **🆕 Enhanced verification provides comprehensive corpus assessment**
7. ✅ Validation provides clear feedback on dataset quality
8. ✅ Fine-tuning completes without technical errors
9. ✅ Generated content noticeably reflects the input writing style
10. ✅ Chat conversations maintain context and support all commands
11. ✅ Session management works (save, resume, export)
12. ✅ Historical author dataset building generates consistent style examples
13. ✅ Error messages are helpful and actionable
14. ✅ The complete workflow takes under 30 minutes (excluding training time)

---

**Ready to test?** Start with `python -m cli.main init` and follow the prompts!

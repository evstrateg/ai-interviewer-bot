# JSON Response Format Specifications

## Core Response Structure

Every AI interviewer response must follow this exact JSON format:

```json
{
  "interview_stage": "stage_code",
  "response": "interviewer_message",
  "metadata": {
    "question_depth": 1-4,
    "completeness": 0-100,
    "engagement_level": "high|medium|low"
  },
  "internal_tracking": {
    "key_insights": ["insight1", "insight2"],
    "examples_collected": 3,
    "follow_up_needed": ["area1", "area2"],
    "stage_transition_ready": false
  }
}
```

## Stage Codes (Mandatory Values)

- `greeting` - Initial rapport building
- `profiling` - Expert background mapping  
- `essence` - Core role philosophy
- `operations` - Daily work processes
- `expertise_map` - Knowledge hierarchy
- `failure_modes` - Error patterns and prevention
- `mastery` - Expert-level insights
- `growth_path` - Professional development timeline
- `wrap_up` - Interview conclusion

## Metadata Field Specifications

### question_depth (Integer 1-4)
- **1**: Initial question on new topic
- **2**: First follow-up for clarification/example
- **3**: Second follow-up for deeper detail  
- **4**: Third+ follow-up for maximum depth

**Usage Rules**:
- Start each new topic at depth 1
- Increment with each follow-up on same topic
- Reset to 1 when changing topics
- Maximum depth 4 before moving on

### completeness (Integer 0-100)
Percentage of information gathered for current stage:
- **0-25%**: Just starting stage, basic questions asked
- **26-50%**: Core topics covered, some examples collected
- **51-75%**: Good depth achieved, multiple examples
- **76-89%**: Nearly complete, minor gaps remain
- **90-100%**: Stage fully complete, ready to transition

**Calculation Guidelines**:
- +20% for each major topic covered in stage
- +10% for each concrete example collected
- +5% for each process description obtained
- +15% for unexpected valuable insights

### engagement_level (String)
Assessment of respondent participation:

**"high"**:
- Responses >200 words regularly
- Provides examples without prompting
- Asks clarifying questions
- Shows enthusiasm/energy
- Volunteers additional information

**"medium"**:
- Adequate response length (50-200 words)
- Answers questions directly
- Stays on topic
- Provides information when requested

**"low"**:
- Brief responses (<50 words)
- Minimal detail provided
- Seems tired/distracted
- Requires multiple prompts for examples

## Internal Tracking Fields

### key_insights (Array of Strings)
Capture unique/valuable insights revealed:
```json
"key_insights": [
  "Uses unconventional client screening method",
  "Identified gap between training and reality",
  "Has unique approach to team conflict resolution"
]
```

### examples_collected (Integer)
Count of concrete examples gathered during interview:
- Increment for each specific real-world example
- Include scenarios, case studies, personal experiences
- Target: 15+ examples total across all stages

### follow_up_needed (Array of Strings)
Areas requiring deeper exploration:
```json
"follow_up_needed": [
  "Decision-making process details",
  "Specific client interaction examples", 
  "Tool usage workflows"
]
```

### stage_transition_ready (Boolean)
Indicates if ready to move to next stage:
- `true`: All criteria met, can advance
- `false`: More work needed in current stage

**Transition Criteria**:
- completeness ≥ 80%
- question_depth reached 3+ on key topics
- examples_collected ≥ minimum for stage
- follow_up_needed list is empty or minor

## Response Message Guidelines

### Message Structure
- Keep individual responses focused and conversational
- Use respondent's name when appropriate
- Reference previous responses to show listening
- End with clear, single question

### Question Formatting
**Single Question Rule**: Each response contains exactly ONE question

**Good Examples**:
```json
{
  "response": "That's a fascinating approach to client onboarding, Maria. Can you walk me through exactly what happens in that first 15-minute conversation?"
}
```

**Bad Examples** (Multiple Questions):
```json
{
  "response": "Interesting! How long does that take? What tools do you use? What if the client objects?"
}
```

### Depth Progression Examples

**Depth 1** (Initial):
```json
{
  "response": "How do you typically handle difficult clients?",
  "metadata": {"question_depth": 1, "completeness": 15, "engagement_level": "medium"}
}
```

**Depth 2** (Example Request):
```json
{
  "response": "That makes sense. Can you give me a specific example of a recent difficult client situation?",
  "metadata": {"question_depth": 2, "completeness": 25, "engagement_level": "medium"}
}
```

**Depth 3** (Process Detail):
```json
{
  "response": "In that situation with the demanding client, walk me through your thought process step-by-step when they first pushed back.",
  "metadata": {"question_depth": 3, "completeness": 40, "engagement_level": "high"}
}
```

**Depth 4** (Expert Insight):
```json
{
  "response": "What did you notice in their behavior that told you to switch strategies at that moment?",
  "metadata": {"question_depth": 4, "completeness": 55, "engagement_level": "high"}
}
```

## Error Handling

### Invalid Stage Code
If invalid stage code provided:
```json
{
  "error": "invalid_stage_code",
  "message": "Stage code must be one of: greeting, profiling, essence, operations, expertise_map, failure_modes, mastery, growth_path, wrap_up",
  "received": "invalid_stage_name"
}
```

### Missing Required Fields
If required fields missing:
```json
{
  "error": "missing_required_fields",
  "message": "Response must include interview_stage, response, and metadata fields",
  "missing_fields": ["interview_stage", "metadata"]
}
```

## Validation Rules

### Pre-Response Validation
Before generating each response, verify:
1. Current stage is valid stage code
2. Question depth is appropriate (1-4)
3. Completeness reflects actual progress
4. Only ONE question in response text
5. Response builds on conversation context

### Post-Response Validation  
After generating response, check:
1. JSON structure is valid
2. All required fields present
3. Metadata values in correct ranges
4. Internal tracking reflects conversation state
5. Stage transition logic is sound

## Integration Notes

### Telegram Bot Implementation
- Parse JSON response to extract user message
- Store metadata for session tracking
- Use internal_tracking for bot state management
- Display only the "response" field to user

### Claude Sonnet-4 Integration
- Include JSON schema in system prompt
- Validate responses before sending to user
- Retry with corrections if JSON invalid
- Log all interactions for analysis

### Analytics and Monitoring
- Track completeness progression across stages
- Monitor engagement_level trends
- Analyze examples_collected per interview
- Measure stage_transition timing
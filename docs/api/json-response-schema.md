# Claude AI Response Schema Documentation

## Overview

This document provides comprehensive documentation for the structured JSON response format used by the AI Interviewer Bot when communicating with Claude AI. The schema ensures consistent, parseable responses that enable sophisticated interview flow control and progress tracking.

## Schema Specification

### Core Response Structure

Every Claude AI response must conform to this JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["interview_stage", "response", "metadata"],
  "properties": {
    "interview_stage": {
      "type": "string",
      "enum": [
        "greeting", "profiling", "essence", "operations", 
        "expertise_map", "failure_modes", "mastery", 
        "growth_path", "wrap_up"
      ],
      "description": "Current interview stage identifier"
    },
    "response": {
      "type": "string",
      "minLength": 10,
      "maxLength": 2000,
      "description": "Interviewer's message to the user"
    },
    "metadata": {
      "type": "object",
      "required": ["question_depth", "completeness", "engagement_level"],
      "properties": {
        "question_depth": {
          "type": "integer",
          "minimum": 1,
          "maximum": 4,
          "description": "Current question depth level (1=initial, 4=maximum depth)"
        },
        "completeness": {
          "type": "integer", 
          "minimum": 0,
          "maximum": 100,
          "description": "Stage completion percentage"
        },
        "engagement_level": {
          "type": "string",
          "enum": ["high", "medium", "low"],
          "description": "Assessment of user engagement"
        }
      }
    },
    "internal_tracking": {
      "type": "object",
      "properties": {
        "key_insights": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Important insights discovered in this exchange"
        },
        "examples_collected": {
          "type": "integer",
          "minimum": 0,
          "description": "Total concrete examples gathered"
        },
        "follow_up_needed": {
          "type": "array", 
          "items": {"type": "string"},
          "description": "Areas requiring deeper exploration"
        },
        "stage_transition_ready": {
          "type": "boolean",
          "description": "Whether ready to advance to next stage"
        }
      }
    },
    "error": {
      "type": "string",
      "enum": ["JSON_PARSE_FAILED", "API_ERROR", "API_RETRY_FAILED"],
      "description": "Error code if response generation failed"
    }
  }
}
```

## Field Specifications

### interview_stage

**Type**: `string` (required)  
**Valid Values**: One of the 9 interview stages  
**Purpose**: Indicates current interview phase

#### Stage Definitions

| Stage | Code | Duration | Purpose |
|-------|------|----------|---------|
| Greeting | `greeting` | 3-5 min | Initial rapport building and orientation |
| Profiling | `profiling` | 10 min | Expert background and experience mapping |
| Essence | `essence` | 15 min | Core role philosophy and approach |
| Operations | `operations` | 20 min | Daily work processes and methodologies |
| Expertise Map | `expertise_map` | 20 min | Knowledge hierarchy and skill assessment |
| Failure Modes | `failure_modes` | 20 min | Common mistakes and prevention strategies |
| Mastery | `mastery` | 15 min | Expert-level insights and best practices |
| Growth Path | `growth_path` | 15 min | Professional development timeline |
| Wrap Up | `wrap_up` | 5 min | Interview conclusion and validation |

### response

**Type**: `string` (required)  
**Length**: 10-2000 characters  
**Purpose**: The interviewer's message displayed to the user

#### Response Guidelines

1. **Single Question Rule**: Each response contains exactly ONE question
2. **Conversational Tone**: Natural, professional, and engaging
3. **Context Awareness**: Reference previous responses to show active listening
4. **Clear Focus**: Each question should have a specific purpose
5. **Progressive Depth**: Build on previous answers for deeper exploration

#### Good Response Examples

```json
{
  "response": "That's a fascinating approach to client onboarding, Maria. Can you walk me through exactly what happens in that first 15-minute conversation with a new client?"
}
```

```json
{
  "response": "You mentioned using unconventional screening methods. What specific techniques have you developed that differ from industry standard practices?"
}
```

#### Response Anti-Patterns

```json
// ❌ Multiple questions
{
  "response": "How long does that process take? What tools do you use? What if the client objects? How do you handle resistance?"
}

// ❌ Too generic
{
  "response": "Tell me more about that."
}

// ❌ No context reference
{
  "response": "What do you do in your job?"
}
```

### metadata

**Type**: `object` (required)  
**Purpose**: Progress tracking and interview flow control

#### question_depth

**Type**: `integer` (1-4, required)  
**Purpose**: Tracks depth of exploration on current topic

| Depth | Description | Usage |
|-------|-------------|-------|
| 1 | Initial question on new topic | Start of new subject area |
| 2 | First follow-up for examples | "Can you give me a specific example?" |
| 3 | Second follow-up for process details | "Walk me through your thought process..." |
| 4 | Third+ follow-up for expert insights | "What patterns have you noticed?" |

**Progression Rules**:
- Start each new topic at depth 1
- Increment with each follow-up on same topic  
- Reset to 1 when changing topics within a stage
- Maximum depth 4 before moving to new topic or stage

#### completeness

**Type**: `integer` (0-100, required)  
**Purpose**: Percentage of information gathered for current stage

| Range | Status | Description |
|-------|--------|-------------|
| 0-25% | Starting | Basic questions asked, minimal information gathered |
| 26-50% | Developing | Core topics covered, some examples collected |
| 51-75% | Substantial | Good depth achieved, multiple examples and processes |
| 76-89% | Nearly Complete | Comprehensive coverage, minor gaps remain |
| 90-100% | Complete | Stage objectives fully met, ready for transition |

**Calculation Guidelines**:
- +20% for each major topic area covered
- +10% for each concrete example with details
- +5% for each process or methodology described
- +15% for unexpected valuable insights discovered

#### engagement_level

**Type**: `string` (required)  
**Valid Values**: `high`, `medium`, `low`  
**Purpose**: Assessment of user participation quality

| Level | Indicators | Response Strategy |
|-------|------------|------------------|
| **high** | • Responses >200 words regularly<br>• Provides examples without prompting<br>• Asks clarifying questions<br>• Shows enthusiasm/energy<br>• Volunteers additional information | • Ask deeper, more complex questions<br>• Explore tangential insights<br>• Move faster through basic topics |
| **medium** | • Adequate response length (50-200 words)<br>• Answers questions directly<br>• Stays on topic<br>• Provides information when requested | • Standard interview pace<br>• Moderate follow-up depth<br>• Occasional engagement prompts |
| **low** | • Brief responses (<50 words)<br>• Minimal detail provided<br>• Seems tired/distracted<br>• Requires multiple prompts for examples | • Shorter, simpler questions<br>• More encouragement and validation<br>• Longer pauses between topics |

### internal_tracking

**Type**: `object` (optional)  
**Purpose**: Bot state management and session tracking

#### key_insights

**Type**: `array` of `string`  
**Purpose**: Capture unique or valuable insights revealed during the exchange

```json
"key_insights": [
  "Uses proprietary client risk assessment algorithm",
  "Identified gap between formal training and real-world application", 
  "Has developed unique conflict resolution approach for remote teams",
  "Discovered cost-saving optimization in deployment pipeline"
]
```

**Guidelines**:
- Record insights that are novel, unexpected, or particularly valuable
- Focus on professional expertise and methodologies
- Include specific techniques, tools, or approaches mentioned
- Capture process innovations or problem-solving strategies

#### examples_collected

**Type**: `integer` (minimum 0)  
**Purpose**: Count of concrete, detailed examples gathered

**What Counts as an Example**:
- Specific real-world scenarios with context
- Detailed case studies with outcomes
- Personal experiences with lessons learned  
- Step-by-step process descriptions with actual instances

**Target**: 15+ examples across entire interview (varies by role complexity)

#### follow_up_needed

**Type**: `array` of `string`  
**Purpose**: Track areas requiring deeper exploration

```json
"follow_up_needed": [
  "Decision-making process for high-stakes client situations",
  "Specific tools and technologies in daily workflow",
  "Team leadership approach during crisis situations",
  "Metrics and measurement strategies for project success"
]
```

**Guidelines**:
- List specific topics that need more depth
- Include areas where user gave surface-level responses
- Note potential knowledge gaps to explore
- Track promised examples or details not yet provided

#### stage_transition_ready

**Type**: `boolean`  
**Purpose**: Indicates readiness to advance to next interview stage

**Transition Criteria**:
- completeness ≥ 80%
- question_depth reached 3+ on key topics within stage
- examples_collected meets minimum threshold for stage
- follow_up_needed list is empty or contains only minor items
- Core stage objectives have been thoroughly explored

## Usage Examples

### Progressive Depth Example

**Depth 1 - Initial Question**
```json
{
  "interview_stage": "operations",
  "response": "How do you typically structure your daily work routine?",
  "metadata": {
    "question_depth": 1,
    "completeness": 35,
    "engagement_level": "medium"
  },
  "internal_tracking": {
    "key_insights": [],
    "examples_collected": 2,
    "follow_up_needed": ["daily routine specifics"],
    "stage_transition_ready": false
  }
}
```

**Depth 2 - Example Request**
```json
{
  "interview_stage": "operations", 
  "response": "That morning routine sounds well-organized. Can you walk me through what a typical Tuesday morning looks like from when you arrive until your first client meeting?",
  "metadata": {
    "question_depth": 2,
    "completeness": 45,
    "engagement_level": "medium"
  },
  "internal_tracking": {
    "key_insights": ["Uses time-blocking methodology"],
    "examples_collected": 3,
    "follow_up_needed": ["specific morning activities", "client meeting preparation"],
    "stage_transition_ready": false
  }
}
```

**Depth 3 - Process Detail**
```json
{
  "interview_stage": "operations",
  "response": "Interesting that you spend 30 minutes on client file review before each meeting. What specific information do you look for during that review time, and how do you organize it?",
  "metadata": {
    "question_depth": 3,
    "completeness": 55,
    "engagement_level": "high"
  },
  "internal_tracking": {
    "key_insights": ["30-minute pre-meeting review protocol", "Systematic client preparation approach"],
    "examples_collected": 4,
    "follow_up_needed": ["information organization system"],
    "stage_transition_ready": false
  }
}
```

**Depth 4 - Expert Insight**
```json
{
  "interview_stage": "operations",
  "response": "You mentioned checking for 'red flags' in client communications. What patterns have you learned to recognize that others might miss?",
  "metadata": {
    "question_depth": 4,
    "completeness": 65,
    "engagement_level": "high"
  },
  "internal_tracking": {
    "key_insights": ["Pattern recognition in client communications", "Early warning system for client issues"],
    "examples_collected": 5,
    "follow_up_needed": [],
    "stage_transition_ready": false
  }
}
```

### Stage Transition Example

```json
{
  "interview_stage": "operations",
  "response": "Thank you for those detailed insights into your daily operations and client management processes. You've shared excellent examples of your systematic approach. Now I'd like to explore your knowledge areas and expertise levels. What would you consider your strongest professional competency?",
  "metadata": {
    "question_depth": 1,
    "completeness": 85,
    "engagement_level": "high"
  },
  "internal_tracking": {
    "key_insights": ["Systematic client management approach", "Proactive issue identification"],
    "examples_collected": 8,
    "follow_up_needed": [],
    "stage_transition_ready": true
  }
}
```

### Error Handling Examples

**JSON Parse Failure Recovery**
```json
{
  "interview_stage": "greeting",
  "response": "I apologize, but I'm having a technical issue with my response formatting. Let me try again: Could you tell me a bit about your professional background and current role?",
  "metadata": {
    "question_depth": 1,
    "completeness": 10,
    "engagement_level": "medium"
  },
  "error": "JSON_PARSE_FAILED"
}
```

**API Error Recovery** 
```json
{
  "interview_stage": "profiling",
  "response": "I'm experiencing some technical difficulties connecting to my AI system. While I work on that, could you elaborate on the last point you made about your experience with team leadership?",
  "metadata": {
    "question_depth": 2,
    "completeness": 25,
    "engagement_level": "medium"
  },
  "error": "API_ERROR"
}
```

## Validation Rules

### Pre-Response Validation

Before generating each response, verify:

1. **Stage Validity**: Current `interview_stage` is valid enum value
2. **Depth Logic**: `question_depth` is appropriate for conversation flow
3. **Completeness Accuracy**: `completeness` reflects actual information gathered
4. **Single Question**: Response contains exactly one question
5. **Context Continuity**: Response builds on previous conversation

### Post-Response Validation

After generating response, validate:

1. **JSON Structure**: Response parses as valid JSON
2. **Required Fields**: All mandatory fields are present
3. **Value Ranges**: Metadata values are within specified ranges  
4. **Tracking Consistency**: Internal tracking reflects conversation state
5. **Transition Logic**: Stage transition decisions are sound

### Common Validation Errors

```json
// ❌ Invalid stage
{
  "error": "invalid_stage_code",
  "message": "Stage 'interviewing' not in valid enum",
  "valid_stages": ["greeting", "profiling", "essence", "operations", "expertise_map", "failure_modes", "mastery", "growth_path", "wrap_up"]
}

// ❌ Missing required fields
{
  "error": "missing_required_fields", 
  "message": "Response missing required fields",
  "missing_fields": ["metadata", "response"]
}

// ❌ Invalid depth value
{
  "error": "invalid_question_depth",
  "message": "question_depth must be 1-4",
  "received_value": 6
}
```

## Integration Notes

### Bot Implementation

```python
def validate_claude_response(response_data: Dict[str, Any]) -> bool:
    """Validate Claude response against schema"""
    required_fields = ['interview_stage', 'response', 'metadata']
    
    # Check required fields
    if not all(field in response_data for field in required_fields):
        return False
    
    # Validate interview stage
    valid_stages = [stage.value for stage in InterviewStage]
    if response_data['interview_stage'] not in valid_stages:
        return False
    
    # Validate metadata
    metadata = response_data['metadata']
    if not (1 <= metadata.get('question_depth', 0) <= 4):
        return False
    
    if not (0 <= metadata.get('completeness', -1) <= 100):
        return False
    
    if metadata.get('engagement_level') not in ['high', 'medium', 'low']:
        return False
    
    return True

def parse_claude_response(response_text: str) -> Dict[str, Any]:
    """Parse and validate Claude response"""
    try:
        # Extract JSON from response
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text.strip()
        
        parsed = json.loads(json_text)
        
        # Validate structure
        if validate_claude_response(parsed):
            return parsed
        else:
            raise ValueError("Invalid response structure")
            
    except Exception as e:
        # Return fallback structure
        return {
            'interview_stage': 'greeting',
            'response': response_text,
            'metadata': {
                'question_depth': 1,
                'completeness': 10,
                'engagement_level': 'medium'
            },
            'error': 'JSON_PARSE_FAILED'
        }
```

### Prompt Engineering

Include this schema documentation in Claude system prompts:

```
You must respond in valid JSON format following this exact structure:

{
  "interview_stage": "current_stage_code",
  "response": "your_interviewer_message", 
  "metadata": {
    "question_depth": 1-4,
    "completeness": 0-100,
    "engagement_level": "high|medium|low"
  },
  "internal_tracking": {
    "key_insights": ["insight1", "insight2"],
    "examples_collected": number,
    "follow_up_needed": ["area1", "area2"],
    "stage_transition_ready": boolean
  }
}

Critical rules:
- interview_stage must be one of: greeting, profiling, essence, operations, expertise_map, failure_modes, mastery, growth_path, wrap_up
- response must contain exactly ONE question
- question_depth: 1=new topic, 2=example request, 3=process detail, 4=expert insight
- completeness: realistic assessment of stage completion (0-100%)
- engagement_level: based on user's response quality and participation
```

This comprehensive schema documentation ensures consistent, structured responses that enable sophisticated interview flow control and meaningful progress tracking throughout the AI-powered interview process.
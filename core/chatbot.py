"""
EducApp AI Tutor - Main Chatbot Logic
Christian AI tutor that integrates biblical worldview across all subjects
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from core.rag_engine import BiblicalWorldviewRAG
from core.guardrails import BiblicalGuardrails
from config.worldview_foundation import WORLDVIEW_STATEMENT, get_biblical_context
import os
from dotenv import load_dotenv

load_dotenv()

class EducAppTutor:
    """
    Faith-Driven AI Tutor for Christian Education
    Biblical worldview integrated across all subjects
    """
    
    def __init__(self):
        # Use Claude 3 Opus
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.3,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        print("Initializing EducApp Tutor...")
        self.rag_engine = BiblicalWorldviewRAG()
        self.guardrails = BiblicalGuardrails()
        self.conversation_history = []
        print("EducApp Tutor ready!\n")
    
    def get_response(self, student_question, subject="general", student_grade=None, user_email=None):
        """
        Main entry point for student questions
        Returns AI tutor response grounded in biblical worldview
        NOW WITH USAGE TRACKING!
        """
        
        print(f"\n📝 Student Question: {student_question}")
        print(f"📚 Subject: {subject}")
        
        # Step 1: Check for topics requiring parental discussion
        guardrail_check = self.guardrails.check_query(student_question)
        
        # Step 2: Retrieve relevant context from knowledge base
        print("🔍 Retrieving biblical worldview context...")
        context = self.rag_engine.retrieve_context(student_question, subject)
        
        # Step 3: Get specific biblical context if applicable
        biblical_principle = None
        if guardrail_check["biblical_context_area"]:
            biblical_principle = get_biblical_context(guardrail_check["biblical_context_area"])
        
        # Step 4: Build system prompt with biblical foundation
        system_prompt = self._build_system_prompt(
            subject, 
            student_grade, 
            context,
            biblical_principle
        )
        
        # Step 5: Generate AI response
        print("💭 Generating response...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Student question: {student_question}")
        ]
        
        try:
            ai_response = self.llm.invoke(messages)
            response = ai_response.content
            
            # NEW: Track token usage and cost
            if user_email:
                try:
                    # Get token counts from response metadata
                    usage = ai_response.response_metadata.get('usage', {})
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
                    
                    if input_tokens > 0 and output_tokens > 0:
                        from core.usage_monitor import track_api_call
                        estimated_cost = track_api_call(
                            user_email=user_email,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            model='claude-3-opus'
                        )
                        
                        print(f"📊 API Call: {input_tokens} in + {output_tokens} out = ${estimated_cost:.4f}")
                
                except Exception as e:
                    print(f"⚠️ Error tracking usage: {e}")
            
            # NEW: Save conversation to history
            if user_email:
                from core.database import save_conversation
                save_conversation(user_email, student_question, response, subject)
            
        except Exception as e:
            response = f"I encountered an error generating a response. Please try again. Error: {str(e)}"
            print(f"❌ Error: {e}")
            return response
        
        # Step 6: Apply guardrails - add parent discussion note if needed
        response = self.guardrails.add_parent_guidance(response, guardrail_check)
        
        # Step 7: Ensure biblical grounding when relevant
        if guardrail_check["biblical_context_area"]:
            response = self.guardrails.ensure_biblical_grounding(
                response, 
                guardrail_check["biblical_context_area"]
            )
        
        # Step 8: Add Scripture reference if relevant and available
        if context["scripture"] and len(context["scripture"]) > 0:
            scripture_excerpt = context["scripture"][0][:300]
            if not guardrail_check["needs_parent_discussion"]:
                response += f"\n\n📖 *Relevant Scripture*: {scripture_excerpt}..."
        
        print("✅ Response generated!\n")
        return response

    def _build_system_prompt(self, subject, grade, context, biblical_principle):
        """
        Create system prompt with biblical worldview and retrieved context
        """
        
        # Build curriculum context section
        curriculum_context = ""
        if context["curriculum"]:
            curriculum_context = "**CURRICULUM CONTEXT:**\n" + "\n\n".join(context["curriculum"][:2])
        
        # Build biblical worldview context section
        worldview_context = ""
        if context["worldview"]:
            worldview_context = "**BIBLICAL WORLDVIEW CONTEXT:**\n" + "\n\n".join(context["worldview"][:2])
        
        # Add specific biblical principle if identified
        biblical_principle_text = ""
        if biblical_principle:
            biblical_principle_text = f"""
**BIBLICAL PRINCIPLE FOR THIS TOPIC:**
Foundation: {biblical_principle['foundation']}
Scripture: {', '.join(biblical_principle['scripture'])}
Approach: {biblical_principle['educational_approach']}
"""
        
        # Build complete system prompt
        system_prompt = f"""
{WORLDVIEW_STATEMENT}

You are a Christian AI tutor helping a student (Grade: {grade or 'Not specified'}) with {subject}.

**YOUR ROLE:**
- Teach {subject} through a biblical worldview
- Help students see how their studies relate to God's truth and character
- Use questions to develop critical thinking (Socratic method)
- Be patient, encouraging, and academically rigorous
- Direct theological and personal questions to parents and church leaders
- Teach biblical truth without compromise

{biblical_principle_text}

{worldview_context}

{curriculum_context}

**WHEN TO DIRECT TO PARENTS:**
- Theological questions requiring pastoral wisdom
- Topics where Christian families may have different biblical applications
- Personal or family matters
- Salvation and personal faith decisions

**RESPONSE STYLE:**
- Start with encouragement when appropriate
- Explain concepts clearly with examples
- Connect subject matter to God's design when natural and relevant
- End with a thought-provoking question when suitable
- Maintain academic excellence alongside biblical integration
- Be concise but thorough

**REMEMBER:**
You serve parents as primary educators. Your role is to support and empower them, not replace them.
The Bible is true and authoritative. Jesus is the Way, the Truth, and the Life.
"""
        
        return system_prompt
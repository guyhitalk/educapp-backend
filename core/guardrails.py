"""
Biblical Guardrails System
Ensures all responses align with biblical Christian worldview
Flags topics where students should consult parents
"""

import re
from config.worldview_foundation import PARENT_DISCUSSION_TOPICS, get_biblical_context

class BiblicalGuardrails:
    """
    Ensures all responses maintain biblical integrity
    Directs students to parents for deeper theological discussions
    """
    
    def __init__(self):
        self.sensitive_keywords = self._build_keyword_list()
    
    def _build_keyword_list(self):
        """Expand discussion topics into keyword triggers"""
        keywords = set()
        
        # Add keywords from parent discussion topics
        for topic in PARENT_DISCUSSION_TOPICS:
            keywords.update(topic.lower().split())
        
        # Add specific theological/worldview trigger words
        keywords.update([
            "salvation", "saved", "born again", "baptism", "communion",
            "rapture", "tribulation", "millennium", "end times",
            "predestination", "election", "free will",
            "catholic", "protestant", "denomination",
            "speaking in tongues", "spiritual gifts", "cessationism"
        ])
        
        return keywords
    
    def check_query(self, query):
        """
        Analyze student query for topics requiring parental discussion
        Returns: dict with flags and guidance
        """
        query_lower = query.lower()
        
        result = {
            "needs_parent_discussion": False,
            "detected_topics": [],
            "biblical_context_area": None
        }
        
        # Check for parent discussion keywords
        for keyword in self.sensitive_keywords:
            if keyword in query_lower:
                result["needs_parent_discussion"] = True
                result["detected_topics"].append(keyword)
        
        # Identify specific biblical context areas
        if any(word in query_lower for word in ["evolution", "darwin", "created", "creation", "origins", "big bang"]):
            result["biblical_context_area"] = "creation_and_science"
        
        elif any(word in query_lower for word in ["bible", "scripture", "god's word", "biblical"]):
            result["biblical_context_area"] = "biblical_authority"
        
        elif any(word in query_lower for word in ["human", "person", "people", "mankind", "man", "woman", "male", "female", "gender"]):
            result["biblical_context_area"] = "human_nature"
        
        elif any(word in query_lower for word in ["right", "wrong", "moral", "ethics", "ethical", "good", "evil", "sin"]):
            result["biblical_context_area"] = "morality_and_ethics"
        
        elif any(word in query_lower for word in ["sex", "sexuality", "marriage", "married", "dating", "relationship"]):
            result["biblical_context_area"] = "human_sexuality_and_marriage"
        
        elif any(word in query_lower for word in ["life", "death", "die", "eternal", "heaven", "hell", "afterlife", "resurrection"]):
            result["biblical_context_area"] = "life_and_death"
        
        return result
    
    def add_parent_guidance(self, response, detected_issues):
        """
        Add appropriate guidance for parent discussion when needed
        """
        
        if detected_issues["needs_parent_discussion"]:
            guidance = "\n\n---\n**Discussion with Parents**: This topic involves important theological matters where Christians may have different understandings. Please discuss this with your parents to understand your family's biblical perspective.\n---"
            response = response + guidance
        
        return response
    
    def ensure_biblical_grounding(self, response, biblical_context_area):
        """
        Verify response includes biblical foundation when needed
        """
        
        # If biblical context is relevant but response doesn't mention God/Bible, add note
        if biblical_context_area and not any(word in response.lower() for word in ["god", "bible", "scripture", "lord", "christ", "jesus"]):
            biblical_note = "\n\n*Biblical Foundation*: Remember that as Christians, we understand this topic through what God's Word teaches us."
            response = response + biblical_note
        
        return response
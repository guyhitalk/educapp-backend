"""
Biblical Worldview Foundation for EducApp
An EdTech platform with a Christian worldview, 
with its principles and values biblically based.
"""

WORLDVIEW_STATEMENT = """
EducApp operates from a biblical Christian worldview:

1. SCRIPTURE: The Bible is God's inspired, inerrant, authoritative Word
2. CREATION: God created all things and sustains creation
3. EDUCATION: Parents are primary educators under God's authority (Deuteronomy 6:6-7)
4. TRUTH: All truth is God's truth - every subject reveals His character
5. PURPOSE: Education serves to love God and neighbor through Christ

We integrate biblical principles across all subjects. The Bible is true and 
authoritative. Jesus is the Way, the Truth, and the Life. We teach what Scripture 
teaches without compromise. Parents guide their children in applying biblical 
truth to daily life.
"""

BIBLICAL_PRINCIPLES = {
    "creation_and_science": {
        "foundation": "God created the heavens and the earth",
        "scripture": ["Genesis 1:1", "Genesis 1:27", "Psalm 19:1", "Romans 1:20", "Colossians 1:16-17"],
        "educational_approach": "The Bible teaches that God created all things, including humans as male and female in His image. This is true. When discussing theories that contradict Scripture, we acknowledge they exist in secular education while teaching what the Bible says is true. Students should discuss these matters with their parents."
    },
    
    "biblical_authority": {
        "foundation": "Scripture is the authoritative Word of God",
        "scripture": ["2 Timothy 3:16-17", "Psalm 119:105", "John 17:17", "John 14:6", "Proverbs 1:7"],
        "educational_approach": "The Bible is God's Word and is true. Jesus said, 'I am the way, and the truth, and the life' (John 14:6). When secular perspectives contradict what Scripture teaches, we teach biblical truth. Parents guide their children in applying God's Word to specific situations."
    },
    
    "human_nature": {
        "foundation": "Humans are created in God's image with inherent dignity",
        "scripture": ["Genesis 1:27", "Genesis 2:18-24", "Psalm 139:13-14"],
        "educational_approach": "God created humans as male and female, bearing His image. This is foundational truth for all discussions of human biology, identity, marriage, and relationships. The Bible is clear on these matters."
    },
    
    "morality_and_ethics": {
        "foundation": "God's character defines good and evil",
        "scripture": ["Exodus 20:1-17", "Matthew 22:37-40", "Romans 13:8-10"],
        "educational_approach": "Right and wrong are defined by God's Word. Biblical morality is true regardless of cultural opinions. We teach what the Bible teaches and direct students to their parents and pastors for applying these truths to specific situations."
    },
    
    "human_sexuality_and_marriage": {
        "foundation": "Marriage is between one man and one woman; sexuality is a gift for marriage",
        "scripture": ["Genesis 1:27", "Genesis 2:24", "Matthew 19:4-6", "1 Corinthians 6:18-20", "Hebrews 13:4"],
        "educational_approach": "The Bible is clear: God created humans male and female, and marriage is between one man and one woman. Sexual intimacy is God's gift for marriage. We teach biblical truth on these matters and encourage students to discuss questions with their parents."
    },
    
    "life_and_death": {
        "foundation": "God is the author of life; eternal life is through Jesus Christ alone",
        "scripture": ["Genesis 2:7", "John 3:16", "John 11:25", "John 14:6", "Acts 4:12", "Romans 6:23"],
        "educational_approach": "The Bible teaches that God gives life, death entered through sin, and eternal life is found only in Jesus Christ. These are biblical truths. Students should discuss these important matters with their parents and church."
    }
}

# Topics where students should be directed to parents for deeper discussion
PARENT_DISCUSSION_TOPICS = [
    "salvation and personal faith decisions",
    "denominational distinctives", 
    "end times theology",
    "church practices and traditions",
    "personal application of biblical commands"
]

def get_biblical_context(topic_area):
    """Retrieve relevant biblical framework for topic"""
    if topic_area in BIBLICAL_PRINCIPLES:
        return BIBLICAL_PRINCIPLES[topic_area]
    return None
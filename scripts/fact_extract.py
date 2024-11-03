import re
def extract_fact(user_input):
    patterns = [
    # Basic identity
    (r'^(i am|i\'m|i was|i will be) (a|an)?\s*(?P<fact>.+)', 'identity'),  # "I am/was/will be a/an Y" or "I'm Y"
    (r'^(my name is|my name was|my name will be) (?P<fact>.+)', 'identity'), # "My name is/was/will be Y"
    (r'^(call me|people call me) (?P<fact>.+)', 'identity'),  # "Call me Y" or "People call me Y"
    (r'^(i have|i had|i will have) (a|an)?\s*(?P<fact>.+)', 'possession'),  # "I have/had/will have a/an Y"

    # Preferences and hobbies
    (r'^(i like|i love|i liked|i loved|i will like|i will love) (?P<fact>.+)', 'preference'),  # "I like/love/liked/loved/will like/love Y"
    (r'^(i enjoy|i\'m fond of|i enjoyed|i was fond of|i will enjoy|i will be fond of) (?P<fact>.+)', 'preference'),  # "I enjoy/am fond of/enjoyed/was fond of/will enjoy/be fond of Y"
    (r'^(my favorite (hobby|pastime|activity) is|was|will be) (?P<fact>.+)', 'preference'),  # "My favorite hobby is/was/will be Y"
    (r'^(i am|i was|i will be) interested in (?P<fact>.+)', 'preference'),  # "I am/was/will be interested in Y"
    (r'^(i prefer|i preferred|i will prefer) (?P<fact>.+)', 'preference'),  # "I prefer/preferred/will prefer Y"

    # Dislikes and aversions
    (r'^(i don\'t like|i dislike|i hate|i didn\'t like|i disliked|i hated|i won\'t like|i will dislike|i will hate) (?P<fact>.+)', 'aversion'),  # "I don't like/dislike/hate/didn't like/disliked/hated/won't like/will dislike/hate Y"
    (r'^(i am not|i was not|i will not be) a fan of (?P<fact>.+)', 'aversion'),  # "I am/was/will not be a fan of Y"
    (r'^(i avoid|i avoided|i will avoid) (?P<fact>.+)', 'aversion'),  # "I avoid/avoided/will avoid Y"

    # Abilities and skills
    (r'^(i can|i am able to|i could|i was able to|i will be able to) (?P<fact>.+)', 'ability'),  # "I can/am able to/could/was able to/will be able to Y"
    (r'^(i know how to|i knew how to|i will know how to) (?P<fact>.+)', 'ability'),  # "I know/knew/will know how to Y"
    (r'^(i am|i was|i will be) good at (?P<fact>.+)', 'ability'),  # "I am/was/will be good at Y"
    (r'^(i have|i had|i will have) experience in (?P<fact>.+)', 'ability'),  # "I have/had/will have experience in Y"

    # Beliefs and values
    (r'^(i believe|i believed|i will believe) in (?P<fact>.+)', 'belief'),  # "I believe/believed/will believe in Y"
    (r'^(i support|i supported|i will support) (?P<fact>.+)', 'belief'),  # "I support/supported/will support Y"
    (r'^(i value|i valued|i will value) (?P<fact>.+)', 'belief'),  # "I value/valued/will value Y"
    (r'^(i stand|i stood|i will stand) for (?P<fact>.+)', 'belief'),  # "I stand/stood/will stand for Y"

    # Emotional states and feelings
    (r'^(i feel|i\'m feeling|i felt|i was feeling|i will feel|i will be feeling) (?P<fact>.+)', 'emotion'),  # "I feel/am feeling/felt/was feeling/will feel/be feeling Y"
    (r'^(i am|i was|i will be) (happy|sad|angry|excited|anxious|worried) (?P<fact>.+)', 'emotion'),  # "I am/was/will be [emotion] Y"
    (r'^(i get|i got|i will get|i become|i became|i will become) (?P<fact>.+)', 'emotion'),  # "I get/got/will get/become/became/will become Y"

    # Daily routines and habits
    (r'^(i usually|i always|i often|i never|i used to|i will usually|i will always|i will often|i will never) (?P<fact>.+)', 'habit'),  # "I usually/always/often/never/used to/will usually/always/often/never Y"
    (r'^(my routine includes|my routine included|my routine will include) (?P<fact>.+)', 'habit'),  # "My routine includes/included/will include Y"
    (r'^(i spend|i spent|i will spend) my time (?P<fact>.+)', 'habit'),  # "I spend/spent/will spend my time Y"

    # Relationships and interactions
    (r'^(i am|i was|i will be) friends with (?P<fact>.+)', 'relationship'),  # "I am/was/will be friends with Y"
    (r'^(i am|i was|i will be) close to (?P<fact>.+)', 'relationship'),  # "I am/was/will be close to Y"
    (r'^(i often talk|i often talked|i will often talk) to (?P<fact>.+)', 'relationship'),  # "I often talk/talked/will often talk to Y"

    # Goals and aspirations
    (r'^(i want|i wanted|i will want) to (?P<fact>.+)', 'goal'),  # "I want/wanted/will want to Y"
    (r'^(i aspire|i aspired|i will aspire) to (?P<fact>.+)', 'goal'),  # "I aspire/aspired/will aspire to Y"
    (r'^(my goal is|my goal was|my goal will be) to (?P<fact>.+)', 'goal'),  # "My goal is/was/will be to Y"
    (r'^(i plan|i planned|i will plan) to (?P<fact>.+)', 'goal'),  # "I plan/planned/will plan to Y"

    # Health and wellness
    (r'^(i am|i was|i will be) (allergic|sensitive) to (?P<fact>.+)', 'health'),  # "I am/was/will be allergic/sensitive to Y"
    (r'^(i (exercise|exercised|will exercise|work out|worked out|will work out) (regularly|often))', 'health'),  # "I exercise/exercised/will exercise/work out/worked out/will work out Y"
    (r'^(i am|i was|i will be) (vegetarian|vegan|pescatarian)', 'diet'),  # "I am/was/will be vegetarian/vegan/pescatarian"

    # Experiences and memories
    (r'^(i remember|i remembered|i will remember) (?P<fact>.+)', 'memory'),  # "I remember/remembered/will remember Y"
    (r'^(i have been|i had been|i will have been) to (?P<fact>.+)', 'experience'),  # "I have been/had been/will have been to Y"
    (r'^(i once|i previously|i will once|i will previously) (?P<fact>.+)', 'experience'),  # "I once/previously/will once/previously Y"

    # Personal possessions and preferences
    (r'^(i own|i owned|i will own|i have|i had|i will have) (a|an)?\s*(?P<fact>.+)', 'possession'),  # "I own/owned/will own/have/had/will have Y"
    (r'^(my favorite (book|movie|song|food|color) is|was|will be) (?P<fact>.+)', 'preference'),  # "My favorite [item] is/was/will be Y"
    (r'^(i prefer|i preferred|i will prefer) (?P<fact>.+)', 'preference'),  # "I prefer/preferred/will prefer Y"
    (r'^(i drive|i drove|i will drive) (?P<fact>.+)', 'activity'),  # "I drive/drove/will drive Y"

    # Work and profession
    (r'^(i work|i worked|i will work) as (?P<fact>.+)', 'profession'),  # "I work/worked/will work as Y"
    (r'^(i am|i was|i will be) employed as (?P<fact>.+)', 'profession'),  # "I am/was/will be employed as Y"
    (r'^(i am|i was|i will be) (a|an)?\s*(?P<fact>.+)', 'profession'),  # "I am/was/will be a Y"
    (r'^(i am|i was|i will be) in the (?P<fact>.+)', 'profession'),  # "I am/was/will be in the Y (industry/field)"

    # Educational background
    (r'^(i study|i studied|i will study) (?P<fact>.+)', 'education'),  # "I study/studied/will study Y"
    (r'^(i have|i had|i will have) a degree in (?P<fact>.+)', 'education'),  # "I have/had/will have a degree in Y"
    (r'^(i graduated|i will graduate) from (?P<fact>.+)', 'education'),  # "I graduated/will graduate from Y"

    # Geography and origin
    (r'^(i am|i was|i will be) from (?P<fact>.+)', 'origin'),  # "I am/was/will be from Y"
    (r'^(i live|i lived|i will live) in (?P<fact>.+)', 'location'),  # "I live/lived/will live in Y"
    (r'^(i was|i will be) born in (?P<fact>.+)', 'origin'),  # "I was/will be born in Y"
    (r'^(i have|i had|i will have) visited (?P<fact>.+)', 'travel'),  # "I have/had/will have visited Y"

    # Miscellaneous
    (r'^(i am|i was|i will be) known for (?P<fact>.+)', 'reputation'),  # "I am/was/will be known for Y"
    (r'^(people describe|described|will describe) me as (?P<fact>.+)', 'reputation'),  # "People describe/described/will describe me as Y"

    # Bot identity questions
    
    (r'^(what is|what\'s) (your|the bot\'s) name\??', 'bot identity'),  # "What is your name?" or "What's your name?"
    (r'^who are you\??', 'bot identity'),  # "Who are you?"

    # Acronym meaning questions
    (r'^(what does|what\'s) (eclipse|e-c-l-i-p-s-e) stand for\??', 'bot identity'),  # "What does Eclipse stand for?" or "What's Eclipse stand for?"
    (r'^explain (the|your) full form of (eclipse|e-c-l-i-p-s-e)\??', 'bot identity')  # "Explain the full form of Eclipse."
]
    for pattern, category in patterns:
        match = re.match(pattern, user_input, re.IGNORECASE)
        if match:
            if 'fact' in match.groupdict():
                fact = match.group('fact').strip().lower()
                return category, fact, pattern
            else:
                return category, None, pattern  # Return None if 'fact' is not found
        
    return None, None, None

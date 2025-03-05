import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

def process_posts(raw_file_path, processed_file_path = None):
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        # print(posts)
        enriched_posts = []
        for post in posts:
           metadata = extract_metadata(post['text'])
           post_with_metadata = post | metadata
           enriched_posts.append(post_with_metadata)
    
    # for eposts in enriched_posts:
    #     print(eposts)    
    unified_tags = get_unified_tags(enriched_posts)
    print("unified_tags",unified_tags)
    for post in enriched_posts:
        current_tags = post['tags']
        # print("current",current_tags)
        new_tags = {unified_tags[tag] for tag in current_tags}
        # print("new",new_tags)
        post['tags'] = list(new_tags)
        
    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4)    
    
def get_unified_tags(posts_with_metadata):
        unique_tags = set()
        for post in posts_with_metadata:
            unique_tags.update(post['tags'])   
        unique_tags_list = ','.join(unique_tags)    
       
        template = '''
        I will give you a list of tags. You need to unify tags with the following requirements:

        1. Tags should be merged into a shorter, standardized list.
        - Example 1: "Jobseekers", "Job Hunting" → "Job Search"
        - Example 2: "Motivation", "Inspiration", "Drive" → "Motivation"
        - Example 3: "Personal Growth", "Personal Development", "Self Improvement" → "Self Improvement"
        - Example 4: "Scam Alert", "Job Scam" → "Scams"

        2. Each tag should follow the **Title Case** convention (e.g., "Motivation", "Job Search").  
        3. The output **must be a valid JSON object only**—no preamble, no explanation.  
        4. Output should have mapping of original tag and the unified tag. 
        For example: {{"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation"}}
        5. Do not print anything else instead of json .  
        {tags}
        '''
        pt = PromptTemplate.from_template(template)
        chain = pt | llm
        response = chain.invoke(input={"tags":str(unique_tags_list)})
        # print("hello",response.content)
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(response.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs 2nd.")
        return res       
     
def extract_metadata(post):
    
    template = '''
    You are given a LinkedIn post. Extract the following details and return only a valid JSON—no preamble, no explanation, and no additional text. 

    1. JSON object must have exactly three keys: `line_count`, `language`, and `tags`.  
    2. `tags` should be an array with a maximum of two relevant tags.  
    3. `language` should be either "English" or "Hinglish" (Hinglish = Hindi + English).  
    4. The response must strictly be a valid JSON object, nothing else.

    Here is the LinkedIn post:
    {post}
    '''
    
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input= {"post":post})
    # print("hello",response.content)
    
    try:
        json_parser= JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException :
        raise OutputParserException("Content to big . Unable to parse jobs.")
    return res 


if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")
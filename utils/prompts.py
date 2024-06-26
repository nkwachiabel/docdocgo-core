from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

from utils.type_utils import BotSettings

REPORT_ASSESSMENT_INSTRUCTION = """\
"REPORT ASSESSMENT: X%", where X is your estimate of how well the query was answered on a scale from 0% to 100%. 
"""

REPORT_ASSESSMENT_INSTRUCTION = """\
"---
REPORT ASSESSMENT: <biggest constructive criticism some hypothetical person making the above query might have for the report, assuming they are difficult to please (AVOID any praise, write ONLY what can be improved, be brief)> <percentage grade they might assign>%"
"""

REPORT_INSTRUCTION = """\
1. Focus on addressing the specific query.
2. Avoid fluff and irrelevant information.
3. Provide available facts, figures, examples, details, dates, locations, etc.
4. If not enough information is available, be honest about it.

The report type should be: {report_type}

Format nicely in Markdown, starting with a title. 

Finish with: \
""" + REPORT_ASSESSMENT_INSTRUCTION

condense_question_template = """Given the following chat history (between Human and you, the Assistant) add context to the last Query from Human so that it can be understood without needing to read the whole conversation: include necessary details from the conversation to make Query completely standalone:
1. First put the original Query as is or very slightly modified (e.g. replacing "she" with who this refers to) 
2. Then, add "[For context: <condensed summary to yourself of the relevant parts of the chat history: if Human asks a question and the answer is clear from the chat history, include it in the summary>]"

Examples of possible Standalone Queries:
- "And then? [For context: Human wrote this in response to your summary of the Big Bang. The general conversation was about the history of the universe.]"
- "How do you know this? [For context: you just summarized relevant parts of your knowledge base answering Human's question about installing Langchain. Briefly, you explained that they need to run "pip install langchain" and likely other libraries like openai, tiktoken, etc.]"
- "hm [For context: Human asked you to write a poem about Washington and you wrote one.]"
- "What was my first message to you? [For context: Human's first message in our chat history was <exact first message from Human in chat history, verbatim>.]

Chat History:
{chat_history}
Last Query from Human: {question}
Standalone version of Last Query: """
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_template)

just_chat_system_template = """You are DocDocGo, a friendly Assistant AI who has been equipped with your own special knowledge base and the ability to do Internet research. For this part of the conversation you won't be retrieving any information from your knowledge base or the Internet. Instead, you will just chat with the user, keeping in mind that you may have used your knowledge base and/or the Internet earlier in the conversation. Use Markdown syntax for your reply."""
JUST_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", just_chat_system_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
)

chat_with_docs_system_template = """You are DocDocGo, a friendly Assistant AI who has been equipped with your own special knowledge base. In response to the user's query you have retrieved the most relevant parts of your knowledge base you could find:

{context}

END OF PARTS OF YOUR KNOWLEDGE BASE YOU RETRIEVED.
Use them for your response ONLY if relevant. Use Markdown syntax for your reply."""
CHAT_WITH_DOCS_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", chat_with_docs_system_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}"),
    ]
)

qa_template_summarize_kb = """You are a helpful Assistant AI who has been equipped with your own special knowledge base. In response to the user's query you have retrieved the most relevant parts of your knowledge base you could find:

{context}

END OF RETRIEVED PARTS OF YOUR KNOWLEDGE BASE.

USER'S QUERY: {question}

YOUR TASK: present the retrieved parts in a digestible way:
1. Start with the TLDR section heading (use Markdown) followed by a quick summary of only the retrieved parts directly relevant to the user's query, if there are any.
2. Continue the rest of your report in Markdown, with section headings. For this part, completely ignore user's query.

YOUR RESPONSE: """
QA_PROMPT_SUMMARIZE_KB = PromptTemplate.from_template(qa_template_summarize_kb)

qa_template_quotes = """You are a helpful Assistant AI who has been equipped with your own special knowledge base. In response to the user's query you have retrieved the most relevant parts of your knowledge base you could find:

{context}

END OF PARTS OF YOUR KNOWLEDGE BASE YOU RETRIEVED.

USER'S QUERY: {question}

YOUR TASK: print any quotes from your knowledge base relevant to user's query, if there are any. Use Markdown syntax for your reply.
YOUR RESPONSE: """
QA_PROMPT_QUOTES = PromptTemplate.from_template(qa_template_quotes)

researcher_template_gpt_researcher = (
    'Information: """{texts_str}"""\n\n'
    "Using the above information, answer the following"
    ' query or task: "{query}" in a detailed report --'
    " The report should focus on the answer to the query, should be well structured, informative,"
    " in depth and comprehensive, with facts and numbers if available and a minimum of 1000 words.\n"
    "You should strive to write the report as long as you can using all relevant and necessary information provided.\n"
    "You must write the report with markdown syntax.\n "
    "Use an unbiased and journalistic tone. \n"
    "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
    "You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n"
    "You MUST write the report in apa format.\n "
    "Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them.\n"
    "Please do your best, this is very important to my career. "
    "Assume that the current date is {datetime}"
)

researcher_template_simple = """<sources>{texts_str}</sources>
Please extract all information relevant to the following query: 
<query>{query}</query>
Write a report, which should be: 1500-2000 words long, in markdown syntax, in apa format. List the references used.
"""
RESEARCHER_PROMPT_SIMPLE = PromptTemplate.from_template(researcher_template_simple)

query_generator_template = """# MISSION
You are an advanced assistant in satisfying USER's information need.

# INPUT 
You are given the following query: {query}
Current timestamp: {timestamp}

# HIGH LEVEL TASK
You don't need to answer the query. Instead, your goal is to determine the information need behind the query and help USER generate a sophisticated plan to satisfy that information need.

# OUTPUT
There are two parts to your output:

## PART 1: Array of google search queries that would be most helpful to perform. These could be sub-questions and/or different ways to rephrase the original query to get an objective, unbiased, up-to-date answer. Use everything you know about information foraging and information literacy in this task.

## PART 2: Brief description of the type of answer/report that will best suit the information need. Examples: "comprehensive report in apa format", "step by step plan of action", "brief one sentence answer", "python code snippet", etc. Use your best judgement to describe the report that will best satisfy the information need. Keep in mind that the report will be written by another LLM, so it can't have images.

Your output should be in JSON following the examples below.

## EXAMPLES OF OUTPUT 

query: "How do I start with Langchain? I want to use it to make a chatbot that I can deploy on a website."
timestamp: Thursday, March 13, 2025, 04:40 PM

output: {{"queries": ["langchain chatbot tutorial March 2025", "langchain getting started", "deploy langchain chatbot on website"],
"report_type": "step by step guide including code snippets, 1500-3000 words"}}


query: "openai news"
timestamp: Saturday, June 22, 2024, 11:01 AM

output: {{"queries": ["openai news June 22 2024", "openai products new features June 2024", "openai organization updates June 2024"],
"report_type": "specifics-dense report rich in facts and figures, 1000-2000 words long"}}


query: "how can I merge two dictionaries in python?"
timestamp: Saturday, November 08, 2025, 06:04 PM

output: {{"queries": ["python merge dictionaries", "python 2025 dictionary union"],
"report_type": "python code snippet with explanation, likely less than 500 words"}}


query: "could you give me a comprehensive medical report on treating chronic migraines?"
timestamp: Monday, August 12, 2024, 11:15 PM

output: {{"queries": ["chronic migraines treatment", "medications for chronic migraines", "non-drug treatments for chronic migraines", "differential diagnosis migraines", "alternative treatments for chronic migraines", "chronic migraines recent research August 2024"],
"report_type": "comprehensive medical report, 1500-2000 words long"}}


query: "how old was John Lennon during the Cuban Missile Crisis?"
timestamp: Tuesday, September 12, 2023, 07:39 AM

output: {{"queries": ["John Lennon birth date", "Cuban Missile Crisis dates"],
"report_type": "brief relevant facts, followed by a formula to calculate the answer, followed by the answer"}}


query: "how old was John Lennon during the Cuban Missile Crisis? I want a report in apa format."
timestamp: Tuesday, September 12, 2023, 07:39 AM

output: {{"queries": ["John Lennon birth date", "Cuban Missile Crisis dates", "John Lennon during Cuban Missile Crisis"],
"report_type": "report in apa format, at least 1000 words long"}}

# YOUR ACTUAL OUTPUT
query: "{query}"
timestamp: {timestamp}

output: """
QUERY_GENERATOR_PROMPT = PromptTemplate.from_template(query_generator_template)

researcher_template_initial_report = """<sources>{texts_str}</sources>
The above information has been retrieved from online sources. Please use it to \
answer the following query: 

<query>{query}</query>

Your answer/report type must be: {report_type}. 

The query and report type provide the most important guidelines, but here are additional general guidelines:
1. Focus on addressing the specific query.
2. Avoid fluff and irrelevant information.
3. Provide available facts, figures, examples, details, dates, locations, etc.
4. If not enough information is available, be honest about it.

Use Markdown syntax for your answer. Start with a title.

Write **only** the report, followed by \
""" + REPORT_ASSESSMENT_INSTRUCTION

researcher_template_initial_report = """\
Here is the scraped content of some online sources.

<sources>{texts_str}</sources>

Using them, please respond to the following query:

<query>{query}</query>

""" + REPORT_INSTRUCTION

RESEARCHER_PROMPT_INITIAL_REPORT = ChatPromptTemplate.from_messages(
    [("user", researcher_template_initial_report)]
)

report_combiner_template = """\
Here are two reports.

1/2:
{report_1}

END OF REPORT 1/2

2/2:
{report_2}

END OF REPORT 2/2

Both reports/answers were written with the aim to best respond to the following query:

<query>{query}</query>

The difference in the reports' content is because they were written using different online sources. Your task: use the above content to write a new version of the report, which will be even better, since it will be indirectly based on twice as many sources as each report individually. Follow these guidelines:

1. Most important: focus on addressing the above query. Provide available facts and figures, if any, and be as specific as possible. Avoid irrelevant information, filler words, and generalizations. If not enough information is available, be honest about it and avoid just filling up space.

2. Use Markdown syntax for your answer. Start with a title.

3. Please write **only** the complete report, followed by \
""" + REPORT_ASSESSMENT_INSTRUCTION

report_combiner_template = """\
Here are two reports compiled from two sets of online sources.

1/2:
{report_1}

END OF REPORT 1/2

2/2:
{report_2}

END OF REPORT 2/2

Using them, please respond to the following query:

<query>{query}</query>

""" + REPORT_INSTRUCTION


REPORT_COMBINER_PROMPT = ChatPromptTemplate.from_messages(
    [("user", report_combiner_template)]
)

searcher_template = """\
Here is the scraped content of some online sources.

<sources>{context}</sources>

Your task: determine if the above sources contain the answer to the following query:

<query>{query}</query>

Answer following one of these scenarios:

1. If the information to answer the query is not available in the sources, write: "ANSWER NOT FOUND".
2. If the sources contain information to fully answer the query, then write: "ANSWER: " followed by the answer. Cite the source where you found the information, including its URL. If more than one source was needed, cite all of them, including their URLs.
3. If the sources contain information to partially answer the query, then write: "PARTIAL ANSWER (<percentage of the answer that was found>)%: " followed by the partial answer. Again, cite the source(s) where you found the information, including their URL(s). 
"""

iterative_report_improver_template = """\
You are ARIA, Advanced Report Improvement Assistant. 

For this task, you can use the following information retrieved from the Internet:

{new_info}

END OF RETRIEVED INFORMATION 

Your task: pinpoint areas of improvement in the report/answer prepared in response to the following query:

{query}

END OF QUERY. REPORT/ANSWER TO ANALYZE:

{previous_report}

END OF REPORT

That report was prepared using information from elsewhere. Your task: combine all of the provided information into a new report. Specifically:

Please write: "ACTION ITEMS FOR IMPROVEMENT:" then provide a numbered list of the individual SOURCEs in the RETRIEVED INFORMATION: first the URL, then specific instructions, in imperative form, for how to use **that particular** URL's CONTENT from above to enhance the report - use word economy, no filler words, and if that particular content is not useful then just write "NOT RELEVANT". Be brief, one numbered list item per SOURCE, with just one or two sentences per item.

Add one more item in your numbered list - any additional instructions you can think of for improving the report/answer, independent of the RETRIEVED INFORMATION, particularly as related to the overall structure of the report, for example how to rearrange sections, what parts to remove, reword, etc. Again, be brief.

After that, write: "NEW REPORT:" and write a new report from scratch in Markdown format, starting with a title. Important: any action items you listed must be **fully** implemented in your report, in which case your report must necessarily be different from the original report. In fact, the new report can be completely different if needed, the only concern is to craft an informative, no-fluff answer to the user's query:

{query}

END OF QUERY. This new report/answer should be: {report_type}. (in case of conflict, user's query takes precedence)

Finish with: """ + REPORT_ASSESSMENT_INSTRUCTION + """\
Don't use Markdown here, only for the new report/answer.

**Important**: don't delete information from the report only because it can't be verified using the provided sources! The information in the report was obtained from previously retrieved sources!
"""

ITERATIVE_REPORT_IMPROVER_PROMPT = ChatPromptTemplate.from_messages(
    [("user", iterative_report_improver_template)]
)

if __name__ == "__main__":
    # Here we can test the prompts
    # NOTE: Run this file as "python -m utils.prompts"
    import os

    from components.llm import get_prompt_llm_chain
    from eval.ai_news_1 import ai_news_1
    from eval.openai_news import openai_news
    from eval.top_russian_desserts import top_russian_desserts

    query_to_context = {
        "top Russian desserts": top_russian_desserts,
        "openai news": openai_news,
        "ai news": ai_news_1,
    }

    prompts_templates_to_test = []  # summarizer_template]

    query = "ai news"
    NUM_ITERATIONS = 2
    for iteration in range(NUM_ITERATIONS):
        print("\n" + "-" * 50)
        print("Iteration", iteration)
        print("-" * 50)
        for i, t in enumerate(prompts_templates_to_test):
            prompt = PromptTemplate.from_template(t)
            chain = get_prompt_llm_chain(
                prompt, BotSettings(), os.getenv("DEFAULT_OPENAI_API_KEY"), stream=True
            )
            print("Prompt", i)
            try:
                chain.invoke({"query": query, "text": query_to_context[query]})
            except Exception as e:
                print("ERROR:", e)

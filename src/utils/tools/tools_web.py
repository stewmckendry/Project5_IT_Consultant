# tools_web.py – External search

# Tool to search the web for relevant information

def search_web(query, max_results=1):
    """
    Searches the web for relevant information using DuckDuckGo.

    Purpose:
    This function uses the DuckDuckGo search engine to find relevant information based on a given query. It returns the snippet of the first search result.

    Parameters:
    query (str): The search query to find relevant information.
    max_results (int): The maximum number of search results to retrieve. Default is 1.

    Workflow:
    1. Initializes a DuckDuckGo search session using DDGS.
    2. Performs a text search with the given query and retrieves up to `max_results` results.
    3. Iterates through the search results and returns the snippet of the first result.
    4. If no results are found, returns a message indicating no relevant results were found.
    5. If an exception occurs during the search, returns a message indicating the web search failed along with the exception message.

    Returns:
    str: The snippet of the first search result, or a message indicating no relevant results were found or the web search failed.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                return r["body"]  # return the first result's snippet
        return "No relevant results found."
    except Exception as e:
        return f"⚠️ Web search failed: {str(e)}"


def search_serpapi(query):    
    """
    Searches the web for relevant information using SerpAPI.

    Purpose:
    This function uses the SerpAPI to perform a web search based on a given query. It retrieves the top result, extracts relevant metadata (title, URL, snippet), and stores the result in the agent's memory for future reference.

    Parameters:
    query (str): The search query to find relevant information.

    Workflow:
    1. Calls the `run` method of the `serpapi` object to perform the search.
    2. Retrieves the list of organic results from the search response.
    3. If results are found:
       - Extracts the title, URL, and snippet of the top result.
       - Stores the metadata in the agent's memory under the "citations" key, categorized by the section name.
       - Returns a formatted string containing the title, URL, and snippet of the top result.
    4. If no results are found, returns a message indicating no web results were found.
    5. If an exception occurs during the search, catches the exception and returns an error message.

    Returns:
    str: A formatted string containing the title, URL, and snippet of the top result, or a message indicating no results were found or an error occurred.
    """
    try:
        results = serpapi.run(query)  # already returns a string summary
        parsed_results = serpapi.results.get("organic_results", [])  # safely get result list

        if parsed_results:
            top_result = parsed_results[0]  # Grab best result
            title = top_result.get("title", "Unknown title")
            url = top_result.get("link", "No link found")
            snippet = top_result.get("snippet", "No snippet provided")

            # Store citation with metadata
            agent.memory.setdefault("citations", {}).setdefault(agent.section_name, []).append({
                "source": "serpapi",
                "query": query,
                "title": title,
                "url": url,
                "snippet": snippet
            })

            return f"📄 {title}\n🔗 {url}\n📌 {snippet}"
        else:
            return "⚠️ No web results found."

    except Exception as e:
        return f"⚠️ SerpAPI error: {str(e)}"


def search_wikipedia(query):    
    """
    Searches Wikipedia for a given query and returns a summary.

    Purpose:
    This function uses the `wikipedia` tool to search for a given query on Wikipedia and retrieve a summary of the relevant information. It handles exceptions to ensure graceful failure in case of errors.

    Parameters:
    query (str): The search query to find relevant information on Wikipedia.

    Workflow:
    1. Calls the `wikipedia.run` method with the provided query to perform the search.
    2. If the search is successful, retrieves and returns the summary as a string.
    3. If an exception occurs during the search, catches the exception and returns an error message.

    Returns:
    str: The summary of the search result from Wikipedia if successful, or an error message if the search fails.
    """
    try:
        results = wikipedia.run(query)  # already returns a string summary
        return results
    except Exception as e:
        return f"⚠️ Wikipedia error: {str(e)}"


def search_arxiv(query):    
    """
    Searches academic papers on arXiv for technical or scientific topics.

    Purpose:
    This function uses the `arxiv_tool` to search for academic papers on arXiv based on a given query. 
    It stores the search results in the agent's memory for later use and returns the results.

    Parameters:
    query (str): The search query to find relevant academic papers on arXiv.

    Workflow:
    1. Calls the `run` method of the `arxiv_tool` with the provided query to perform the search.
    2. If the search is successful:
       - Stores the search results in the agent's memory under the "citations" key, categorized by the section name.
       - Returns the search results.
    3. If an exception occurs during the search, catches the exception and returns an error message.

    Returns:
    str: The search results from arXiv if successful, or an error message if the search fails.
    """
    try:
        results = arxiv_tool.run(query)
        
        # Store citation for later use
        agent.memory.setdefault("citations", {}).setdefault(agent.section_name, []).append({
            "source": "arxiv",
            "query": query,
            "result": results
        })

        return results
    except Exception as e:
        return f"⚠️ Arxiv search failed: {str(e)}"


def should_search_arxiv(section_text, model="gpt-3.5-turbo"):
    """
    Determines whether academic research or scientific citations could enhance the credibility of a report section.

    Purpose:
    This function evaluates a given section of an IT consulting report to decide if referencing academic research or scientific citations would improve its credibility. It uses an AI model to analyze the section and provide a decision along with a reason.

    Parameters:
    section_text (str): The text of the section to be evaluated.
    model (str): The name of the AI model to use for evaluation. Default is "gpt-3.5-turbo".

    Workflow:
    1. Constructs a prompt instructing the AI model to analyze the section and determine if academic research would enhance its credibility.
    2. Sends the prompt to the AI model using the `call_openai_with_tracking` function.
    3. Extracts the decision (YES or NO) and the reason from the AI model's response using regular expressions.
    4. If the decision or reason cannot be extracted, defaults to "NO" with a generic reason.
    5. Returns the decision as a boolean and the reason as a string.

    Returns:
    tuple:
        - bool: `True` if academic research is recommended, `False` otherwise.
        - str: The reason for the decision.
    """
    prompt = (
        "You're reviewing a section of an IT consulting report.\n"
        "Determine whether academic research or scientific citations could enhance the credibility of this section.\n\n"
        f"Section:\n{section_text}\n\n"
        "Respond only with YES or NO and one short reason. Format:\n"
        "Decision: YES or NO\nReason: ..."
    )
    messages = [{"role": "user", "content": prompt}]
    response = call_openai_with_tracking(messages, model=model)
    
    decision_match = re.search(r"Decision:\s*(YES|NO)", response, re.IGNORECASE)
    reason_match = re.search(r"Reason:\s*(.+)", response, re.IGNORECASE)
    
    decision = decision_match.group(1).strip().upper() if decision_match else "NO"
    reason = reason_match.group(1).strip() if reason_match else "No reason given."
    
    return decision == "YES", reason

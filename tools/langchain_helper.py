# Do this so we can see exactly what's going on under the hood
# from langchain.globals import set_debug
#
# set_debug(True)

from datetime import datetime
import pytz

from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.tools import Tool as LangChainTool

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent_toolkits import PlayWrightBrowserToolkit
from langchain.tools.playwright.utils import (
    create_sync_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.
)

# Main executable code
def daily_synopsis(temperature=0, model="gpt-4-1106-preview"):
    # Instantiations and function calls
    llm = ChatOpenAI(temperature=temperature, model=model)

    sync_browser = create_sync_playwright_browser()
    toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
    tools = toolkit.get_tools()

    search = GoogleSerperAPIWrapper()

    tools.append(
        LangChainTool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions",
        )
    )


    agent_chain = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=True, handle_parsing_errors=True
    )



    my_date = datetime.now(pytz.timezone('US/Eastern'))

    result = agent_chain.run(f"""Create synopsis of the stock market today ({my_date.strftime('%Y-%m-%d')}). Use 
    online search tools to find several sources and make sure to cite them. The report should be succinct with 
    important data presented. Search for numerical details when they are not found. Research the current sentiment 
    of investors and present a synopsis.""")

    print(result)


if __name__ == "__main__":
    print(daily_synopsis(temperature=0, model="gpt-4-1106-preview"))
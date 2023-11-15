# Do this so we can see exactly what's going on under the hood
# from langchain.globals import set_debug
#
# set_debug(True)

from datetime import datetime
import pytz
import asyncio

from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.tools import Tool as LangChainTool
from langchain.agents.agent_toolkits import PlayWrightBrowserToolkit

from playwright.async_api import async_playwright
from playwright.async_api import Browser as AsyncBrowser
from playwright.sync_api import Browser as SyncBrowser
from typing import List
from langchain.tools.playwright.utils import run_async

"""Util that calls AlphaVantage for Daily Adjusted Time Series."""
from typing import Any, Dict, Optional

import requests

from langchain.pydantic_v1 import BaseModel, Extra, root_validator
from langchain.utils import get_from_dict_or_env


class AlphaVantageDailyAdjustedAPIWrapper(BaseModel):
    """Wrapper for AlphaVantage API for Daily Adjusted Time Series.

    Docs for using:

    1. Go to AlphaVantage and sign up for an API key
    2. Save your API KEY into ALPHAVANTAGE_API_KEY env variable
    """

    alphavantage_api_key: Optional[str] = None

    class Config:
        extra = Extra.forbid

    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        values["alphavantage_api_key"] = get_from_dict_or_env(
            values, "alphavantage_api_key", "ALPHAVANTAGE_API_KEY"
        )
        return values

    def _get_daily_adjusted(
            self, symbol: str, outputsize: Optional[str] = "compact", datatype: Optional[str] = "json"
    ) -> Dict[str, Any]:
        """Make a request to the AlphaVantage API to get the daily adjusted time series."""
        response = requests.get(
            "https://www.alphavantage.co/query/",
            params={
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol,
                "outputsize": outputsize,
                "datatype": datatype,
                "apikey": self.alphavantage_api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")

        return data

    def run(self, symbol: str, outputsize: Optional[str] = "compact", datatype: Optional[str] = "json") -> str:
        """Get the daily adjusted time series for a specified equity symbol."""
        data = self._get_daily_adjusted(symbol, outputsize, datatype)
        return data


def create_async_playwright_browser(
        headless: bool = True,
        args: List[str] = None) -> AsyncBrowser:
    """
    Create an async playwright browser.

    Args:
        headless: Whether to run the browser in headless mode. Defaults to True.
        args: A list of arguments for the browser instance.

    Returns:
        AsyncBrowser: The playwright browser.
    """
    browser = run_async(async_playwright().start())
    return run_async(browser.chromium.launch(headless=headless, args=args))


def create_sync_playwright_browser(
        headless: bool = True,
        args: List[str] = None) -> SyncBrowser:
    """
    Create a playwright browser.

    Args:
        headless: Whether to run the browser in headless mode. Defaults to True.

    Returns:
        SyncBrowser: The playwright browser.
    """
    from playwright.sync_api import sync_playwright

    browser = sync_playwright().start()
    return browser.chromium.launch(headless=headless, args=args)


def get_prompt(my_date):
    return f"""Act as my investment advisor and create a detailed report of the current US stock market ({my_date.strftime('%Y-%m-%d %H:%M:%S %z')}). 
            Use the search tool to find sufficient sources. 
            Scrape cnbc.com and marketwatch.com
            The report should contain many market details and updates. 
            If there is an issue retrieving data, try again several times, finding a different URL if necessary.
            Ask many targeted questions when using search before creating the synopsis. 
            Note whether the market is open, or when it is anticipated to open.
            The tool_schema should always include action."""

def daily_synopsis_async(temperature=1, model="gpt-4-1106-preview", verbose=True):
    # Instantiations and function calls
    llm = ChatOpenAI(temperature=temperature, model=model)

    # Use the async version of the Playwright browser toolkit
    async_browser = create_async_playwright_browser(args=["--disable-gpu", "--single-process"])
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
    tools = toolkit.get_tools()
    # too many hyperlinks. Causes tokens to max out.
    # tools.pop(4)

    search = GoogleSerperAPIWrapper()

    tools.append(
        LangChainTool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted "
                        "questions.",
        )
    )

    agent_chain = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=verbose, handle_parsing_errors=True
    )

    my_date = datetime.now(pytz.timezone('US/Eastern'))

    result = agent_chain.arun(get_prompt(my_date))

    return result

def daily_synopsis(temperature=1, model="gpt-4-1106-preview", verbose=True):
    # Instantiations and function calls
    llm = ChatOpenAI(temperature=temperature, model=model)

    # Use the async version of the Playwright browser toolkit
    sync_browser = create_sync_playwright_browser(args=["--disable-gpu", "--single-process"])
    toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
    tools = toolkit.get_tools()
    # too many hyperlinks. Causes tokens to max out.
    # tools.pop(4)

    search = GoogleSerperAPIWrapper()

    tools.append(
        LangChainTool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted "
                        "questions.",
        )
    )

    agent_chain = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=verbose, handle_parsing_errors=True
    )

    my_date = datetime.now(pytz.timezone('US/Eastern'))

    result = agent_chain.run(get_prompt(my_date))

    return result


def entry_point(temperature=1, model="gpt-4-1106-preview", verbose=True):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(daily_synopsis_async(temperature=temperature, model=model, verbose=verbose))
    except RuntimeError as e:
        # This handles the "This event loop is already running" error.
        if "already running" in str(e):
            # If the loop is already running, we can directly call the coroutine.
            # But this should be done with caution and understanding of the implications.
            return asyncio.run_coroutine_threadsafe(
                daily_synopsis_async(temperature=temperature, model=model, verbose=verbose),
                asyncio.get_event_loop()).result()
        else:
            raise


if __name__ == "__main__":
    # print(entry_point())
    print(daily_synopsis())

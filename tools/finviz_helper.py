import pandas as pd
from pyfinviz.screener import Screener
import requests
from time import sleep


def get_sp500_tickers_sectors():
    """
    Retrieves tickers and sector data for S&P 500 components using the Finviz screener.

    Returns:
        DataFrame: A pandas DataFrame containing the tickers and sector information of the S&P 500 components.
    """
    options = [Screener.IndexOption.S_AND_P_500]
    screener = Screener(filter_options=options, view_option=Screener.ViewOption.OVERVIEW,
                        pages=[x for x in range(1, 27)])
    df = pd.concat(screener.data_frames.values())
    return df


def get_nasdaq100_tickers_sectors():
    """
    Retrieves tickers and sector data for NASDAQ 100 components using the Finviz screener.

    Returns:
        DataFrame: A pandas DataFrame containing the tickers and sector information of the NASDAQ 100 components.
    """
    options = [Screener.IndexOption.NASDAQ_100]
    screener = Screener(filter_options=options, view_option=Screener.ViewOption.OVERVIEW,
                        pages=[x for x in range(1, 7)])
    df = pd.concat(screener.data_frames.values())
    return df


def get_djia_tickers_sectors():
    """
    Retrieves tickers and sector data for Dow Jones Industrial Average (DJIA) components using the Finviz screener.

    Returns:
        DataFrame: A pandas DataFrame containing the tickers and sector information of the DJIA components.
    """
    options = [Screener.IndexOption.DJIA]
    screener = Screener(filter_options=options, view_option=Screener.ViewOption.OVERVIEW,
                        pages=[x for x in range(1, 3)])
    df = pd.concat(screener.data_frames.values())
    return df


def get_screener(api_token, layout='Overview', symbols=None, sleep_secs=0):
    """
    Retrieves screener data from Finviz based on the provided parameters.

    Args:
        api_token (str): API token for authentication.
        layout (str): The layout of the screener data to be retrieved. Defaults to 'Overview'.
        symbols (list of str, optional): List of symbols to filter the screener data. Defaults to None.
        sleep_secs (int): Time in seconds to sleep after making the request. Defaults to 0.

    Returns:
        Response: The response object from the Finviz request.
    """
    layout_value = get_screener_layout(layout)
    filters = f"v={layout_value}"
    if symbols:
        filters += "&t=" + ",".join(symbols)
    response = get_request(api_token, filters, sleep_secs=sleep_secs)
    return response


def get_groups(api_token, group_name='sector',
               layout='Overview', subgroup_name=None, sleep_secs=0):
    """
    Retrieves group data from Finviz based on the provided parameters.

    Args:
        api_token (str): API token for authentication.
        group_name (str): The name of the group for which data is to be retrieved. Defaults to 'sector'.
        layout (str): The layout of the group data to be retrieved. Defaults to 'Overview'.
        subgroup_name (str, optional): The name of the subgroup within the group. Defaults to None.
        sleep_secs (int): Time in seconds to sleep after making the request. Defaults to 0.

    Returns:
        Response: The response object from the Finviz request.
    """
    layout_value = get_group_layout(layout)
    filters = f"g={verify_group_name(group_name)}&v={layout_value}"
    if subgroup_name:
        filters += f"&sg={verify_subgroup_name(group_name, subgroup_name)}"
    response = get_request(api_token, filters, sleep_secs=sleep_secs)
    return response


def verify_group_name(group_name):
    """
    Verifies if the provided group name is valid.

    Args:
        group_name (str): The group name to be verified.

    Returns:
        str: The verified group name if valid, otherwise defaults to 'sector'.
    """
    valid_groups = ['sector', 'industry', 'country', 'capitalization']
    return group_name if group_name in valid_groups else 'sector'


def verify_subgroup_name(group_name, subgroup_name):
    """
    Verifies if the provided subgroup name is valid for the given group name.

    Args:
        group_name (str): The group name.
        subgroup_name (str): The subgroup name to be verified.

    Returns:
        str: The verified subgroup name if valid, otherwise defaults to 'basicmaterials'.

    Raises:
        Exception: If subgroups are applied to groups other than 'industry'.
    """
    if group_name != 'industry':
        raise Exception('Subgroups only apply to the \"industry\" group.')
    valid_subgroups = [
        'basicmaterials', 'communicationservices', 'consumercyclical', 'consumerdefensive',
        'energy', 'financial', 'healthcare', 'industrials', 'realestate', 'technology', 'utilities'
    ]
    return subgroup_name if subgroup_name in valid_subgroups else 'basicmaterials'


def get_group_layout(layout):
    """
    Retrieves the layout code for the given layout name.

    Args:
        layout (str): The layout name.

    Returns:
        str: The corresponding layout code.
    """
    layout_map = {
        'Overview': '110',
        'Valuation': '120',
        'Performance': '140',
        'Custom': '150',
    }
    return layout_map.get(layout, '110')


def get_request(api_token, filters, sleep_secs=0):
    """
    Makes a GET request to the Finviz API with the given filters.

    Args:
        api_token (str): API token for authentication.
        filters (str): Filters to apply in the request.
        sleep_secs (int): Time in seconds to sleep after making the request. Defaults to 0.

    Returns:
        Response: The response object from the request.
    """
    URL = f"https://elite.finviz.com/export.ashx?{filters}&auth={api_token}"
    response = requests.get(URL)
    sleep(sleep_secs)
    return response


def get_screener_layout(layout):
    """
    Retrieves the screener layout code for the given layout name.

    Args:
        layout (str): The layout name.

    Returns:
        str: The corresponding screener layout code.
    """
    layout_map = {
        'Overview': '111',
        'Valuation': '121',
        'Financial': '161',
        'Ownership': '131',
        'Performance': '141',
        'Technical': '171',
        'Custom': '151',
    }
    return layout_map.get(layout, '111')

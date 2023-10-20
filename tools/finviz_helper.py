import requests
from time import sleep


def get_screener(api_token, layout='Overview', symbols=None, sleep_secs=0):
    layout_value = get_screener_layout(layout)
    filters = f"v={layout_value}"
    if symbols:
        filters += "&t=" + ",".join(symbols)
    response = get_request(api_token, filters, sleep_secs=sleep_secs)
    return response


def get_groups(api_token, group_name='sector',
               layout='Overview', subgroup_name=None, sleep_secs=0):
    layout_value = get_group_layout(layout)
    filters = f"g={verify_group_name(group_name)}&v={layout_value}"
    if subgroup_name:
        filters += f"&sg={verify_subgroup_name(group_name, subgroup_name)}"
    response = get_request(api_token, filters, sleep_secs=sleep_secs)
    return response


def verify_group_name(group_name):
    valid_groups = ['sector', 'industry', 'country', 'capitalization']
    return group_name if group_name in valid_groups else 'sector'


def verify_subgroup_name(group_name, subgroup_name):
    if group_name != 'industry':
        raise Exception('Subgroups only apply to the \"industry\" group.')
    valid_subgroups = [
        'basicmaterials', 'communicationservices', 'consumercyclical', 'consumerdefensive',
        'energy', 'financial', 'healthcare', 'industrials', 'realestate', 'technology', 'utilities'
    ]
    return subgroup_name if subgroup_name in valid_subgroups else 'basicmaterials'


def get_group_layout(layout):
    layout_map = {
        'Overview': '110',
        'Valuation': '120',
        'Performance': '140',
        'Custom': '150',
    }
    return layout_map.get(layout, '110')


def get_request(api_token, filters, sleep_secs=0):
    URL = f"https://elite.finviz.com/export.ashx?{filters}&auth={api_token}"
    response = requests.get(URL)
    sleep(sleep_secs)
    return response


def get_screener_layout(layout):
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

from dotenv import load_dotenv
import os
from tools.ameritrade_helper import get_specified_account, analyze_tda

load_dotenv()

tda_api_key = os.getenv('TDA_API_KEY')
tda_account_id = os.getenv('TDA_ACCOUNT_ID')
account = get_specified_account(account_id=tda_account_id,
                                api_key=tda_api_key,
                                chrome_driver_path='../tools/chromedriver',
                                token_path='../res/token.json')
investments = analyze_tda(account)
investments

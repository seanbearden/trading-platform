# trading-platform
A platform for monitoring and assessing various trading activities.

This Python project is meant to assist my option-trading endeavors using TD Ameritrade. 

Need to determine



## Requirements
* chromedriver in path: https://chromedriver.chromium.org. Confirm that version matches Google Chrome version.
* TD Ameritrade API key: https://developer.tdameritrade.com
* Alphavantage API key: https://www.alphavantage.co/support/#api-key
* OpenAI API key: https://platform.openai.com/account/api-keys

## Set Up
1. Save Alphavantage API key to .env as `ALPHAVANTAGE_API_KEY` for local usage. Save the key to AWS System 
   Manager->Parameter Store as `ALPHAVANTAGE_API_KEY` for AWS Lambda usage.
2. Set Up Amazon Simple Email Service. 
3. Store from email in AWS System 
   Manager->Parameter as `FROM_EMAIL`. Store to emails in AWS System 
   Manager->Parameter as a stringList named `TO_EMAILS`. Use commas to separate emails, no spaces.
4. Build and deploy using SAM, must specify Docker context `DOCKER_ENDPOINT`. Follow [these](https://github.
   com/aws/aws-sam-cli/issues/4329#issuecomment-1732670902) instructions to determine location of host.
    ```bash
    DOCKER_HOST=DOCKER_ENDPOINT sam build --use-container -t template.yaml
    DOCKER_HOST=DOCKER_ENDPOINT sam deploy --guided

    ```
5. Test on API using body:
   ```json
    {
        "report_type": "stock_analysis",
        "send_email": true,
        "symbol": "MSFT"
    }
    ```
   

## Task 1
### Pull portfolio details from Ameritrade
* Connect to Ameritrade API
* Present investments on dashboard with filtering options.

## Task 2
### Create log of intent with purchases, specifically exit signals.

## Task 3
### Create ability to manually enter order and trigger text alerts.
* Vital to this project is an alert system. AWS products will be utilized in building the alert system. I need an 
MySQL RDS, and a lambda function that runs on a schedule.
* Need basic interface on a Dash/Flask app. Need symbol, option contract date and strike, order price and quantity.
* Send texts via Twilio to interested parties.
* All entries should be logged in an RDS.
* Verification of entries using Ameritrade
* Confirmation or error presented to user

## Task 4
### Notes
* Need to make notes for trades
* 

## Task 5
### reporting



## TODO:
* display open orders
* display positions without orders
* pull live alpha vantage data
* Display index data
* Twilio interaction
* chatgpt monitoring and text interaction

## Chromedriver 
Need to downgrade Chrome and prevent from updating following these instructions: https://support.google.com/chrome/a/answer/7591084?hl=en#zippy=%2Cturn-off-updates%2Ccreate-a-new-property-list-file


## Code Coverage

Code coverage measures the amount of your source code that is covered by your test suite. It's a useful metric that can help you identify areas of your code that might not be adequately tested. There are several tools available for measuring code coverage in Python, but one of the most commonly used is `coverage.py`.

Here's a basic outline of how to use `coverage.py` with pytest:

1. **Install coverage.py**: If you haven't already, you can install `coverage.py` using pip:

   ```bash
   pip install coverage
   ```
   
2. **Run your tests with coverage**: Use the `coverage run` command to run your tests and collect coverage data. If you're using pytest to run your tests, it would look something like this:

   ```bash
   coverage run -m pytest
   ```
   
   This will run your tests with pytest and collect coverage data.

3. **View the coverage report**: After running your tests with coverage, you can view a simple report in your console with the `coverage report` command:

   ```bash
   coverage report -m
   ```
   
   This will print a report showing the coverage for each module in your project.

4. **Generate a detailed HTML report**: For a more detailed, visual report, you can generate an HTML report using the `coverage html` command:

   ```bash
   coverage html
   ```
   
   This will generate an HTML report in a directory named `htmlcov`. You can view the report by opening the `index.html` file in this directory in your web browser.

These are the basics of using `coverage.py` to measure test coverage in Python. The tool also offers many more advanced features, like annotating your source code with coverage information, measuring branch coverage, and setting a minimum required coverage. You can learn more about these features in the `coverage.py` documentation.
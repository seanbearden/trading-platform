import pandas as pd
from alpha_vantage.techindicators import TechIndicators
# from alpha_vantage.timeseries import TimeSeries
import boto3
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from io import StringIO
import json
# import os
# import tempfile
from tools import analyze_tda, find_last_crossover, get_screener
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Table,
    TableStyle,
    PageBreak,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
import seaborn as sns


def lambda_handler(event, context):
    # Parse input
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)

    tmp_files = []
    if body:
        # Create PDF
        pdf_path = "/tmp/report.pdf"
        tmp_files.append(pdf_path)

        # get api keys
        ssm = boto3.client('ssm')
        parameter = ssm.get_parameter(Name='ALPHAVANTAGE_API_KEY', WithDecryption=True)
        alphavantage_api_key = parameter['Parameter']['Value']
        parameter = ssm.get_parameter(Name='FINVIZ_API_KEY', WithDecryption=True)
        finviz_api_key = parameter['Parameter']['Value']

        # account = get_specified_account_with_aws()
        with open('../../res/samples/account.json', 'r') as file:
            account = json.load(file)

        account_analysis = analyze_tda(account)
        # option_table_cols = ["Symbol", "Type", "MACD Hist", "Crossover", "RSI", "Last RSI Signal",
        #                      "RSI Signal Date"]
        option_table_dict = {}

        # option_table = [option_table_cols]
        for contract in account_analysis['OPTION']['positions']:
            instrument = contract['instrument']
            put_call = instrument['putCall']
            underlying_symbol = instrument['underlyingSymbol']

            ti = TechIndicators(key=alphavantage_api_key, output_format='pandas')

            macd_data, meta_macd_data = ti.get_macd(
                symbol=underlying_symbol, interval='daily', fastperiod=12, slowperiod=26, signalperiod=9,
                series_type='close'
            )
            # Usage:
            last_crossover_date = find_last_crossover(macd_data)

            rsi_oversold_threshold = 30
            rsi_overbought_threshold = 70
            crossover_days_threshold = 7

            rsi_data, meta_rsi_data = ti.get_rsi(
                symbol=underlying_symbol, interval='daily', time_period=14, series_type='close'
            )

            reversed_rsi_data = rsi_data.loc[::-1]
            current_rsi = reversed_rsi_data.iloc[0]['RSI']
            most_recent_signal = None
            threshold_index = reversed_rsi_data.iloc[0].name
            if rsi_oversold_threshold <= current_rsi <= rsi_overbought_threshold:
                for index, row in reversed_rsi_data.iterrows():
                    if row['RSI'] > rsi_overbought_threshold:
                        most_recent_signal = 'overbought'
                        threshold_index = index
                        break
                    elif row['RSI'] < rsi_oversold_threshold:
                        most_recent_signal = 'oversold'
                        threshold_index = index
                        break
            elif current_rsi < rsi_oversold_threshold:
                most_recent_signal = 'oversold'
            else:
                most_recent_signal = 'overbought'

            option_table_dict[instrument['symbol']] = {
                "Symbol": underlying_symbol,
                "Type": put_call,
                "Market": contract['marketValue'],
                "MACD Hist": macd_data.iloc[0]['MACD_Hist'],
                "Crossover": last_crossover_date,
                "RSI": current_rsi,
                "RSI Signal": most_recent_signal,
                "RSI Date": threshold_index.strftime('%m-%d-%Y')
            }

            # break


        # Create a BaseDocTemplate
        doc = BaseDocTemplate("example.pdf", pagesize=letter)

        # Define a page template with a footer
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
        page_template = PageTemplate(id='PageTemplate', frames=[frame], onPage=header_footer)
        doc.addPageTemplates([page_template])

        # # Create a SimpleDocTemplate
        # doc = SimpleDocTemplate("example.pdf", pagesize=letter)

        # Title page content
        styles = getSampleStyleSheet()

        # Modify the existing styles to be center-aligned
        styles['Title'].alignment = 1  # 1 is the code for center alignment
        styles['Heading1'].alignment = 1
        styles['Heading2'].alignment = 1

        title = Paragraph("Daily Trading Report", styles['Title'])
        sub_title = Paragraph(pd.Timestamp.now(tz='US/Eastern').strftime('%m-%d-%Y'), styles['Heading1'])
        author = Paragraph("Author: Sean R.B. Bearden", styles['Heading2'])
        logo = Image("image/logo.png", width=100, height=100)

        option_table_df = pd.DataFrame.from_dict(option_table_dict, orient='index')
        screener = get_screener(finviz_api_key,
                                layout='Overview',
                                symbols=list(option_table_df['Symbol'].unique()),
                                sleep_secs=0)
        csvStringIO = StringIO(screener.text)
        screener_df = pd.read_csv(csvStringIO, sep=",", header=0, index_col='No.')

        # Apply a basic table style
        style_commands = [('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            # ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ]

        datetime_now = pd.Timestamp.now(tz='US/Eastern')
        # Iterate through the rows of the table, checking the RSI value in each row
        for i, row in option_table_df.reset_index().iterrows():
            rsi_value = row['RSI']
            if rsi_oversold_threshold < rsi_value < rsi_overbought_threshold:
                bg_color = colors.lightgreen  # Green background
            else:
                bg_color = colors.indianred  # Red background for RSI <= 30 or RSI >=70
            style_commands.append(('BACKGROUND', (5, i+1), (5, i+1), bg_color))

            macd_crossover_date = row['Crossover']
            if (datetime_now.tz_localize(tz=None) - macd_crossover_date).days < crossover_days_threshold:
                bg_color = colors.indianred  # Recent MACD Crossover
            else:
                bg_color = colors.grey
            style_commands.append(('BACKGROUND', (4, i+1), (4, i+1), bg_color))

        table_style = TableStyle(style_commands)
        option_table_df['Crossover'] = option_table_df['Crossover'].dt.strftime('%m-%d-%Y')
        option_table_df.sort_values('Symbol', inplace=True)
        option_table = [list(option_table_df.columns)] + option_table_df.values.tolist()
        table = Table(option_table, repeatRows=1)
        table.setStyle(table_style)

        option_table_df = option_table_df.merge(screener_df[['Ticker', 'Sector']], left_on='Symbol',
                                                right_on='Ticker', how='left')

        # Create the boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Sector', y='Market', data=option_table_df, hue='Type')

        # Set the title and labels
        plt.title('Option Market Value by Sector')
        plt.xlabel('Sector')
        plt.xticks(rotation=45)  # This will rotate the labels by 45 degrees.
        plt.ylabel('Market Value')

        # Show the plot
        plt.tight_layout()
        plt.savefig("box_plot.png")
        # plt.show()

        # # Scatter plot for the third page
        # fig, ax = plt.subplots()
        # # Assuming x and y are your data
        # x = [1, 2, 3, 4, 5]
        # y = [10, 20, 15, 25, 30]
        # ax.scatter(x, y)
        # plt.savefig("scatter_plot.png")

        box_plot = Image("box_plot.png", width=50*10, height=50*6)

        # Build the document
        # doc.build([title, sub_title, author, logo, PageBreak(), table, PageBreak(), scatter_plot], onPage=footer)
        doc.build([title, sub_title, author, logo, PageBreak(), table, PageBreak(), box_plot])

        return {'statusCode': 200, 'body': 'Report created successfully, but not sent!'}
    else:
        return {
            'statusCode': 400,
            'body': 'ERROR'
        }


# Function to draw the header and footer on each page
def header_footer(canvas, doc):
    if doc.page != 1:  # Skip header and footer on the first page
        # Draw the header
        logo_path = "image/logo.png"  # Path to your logo file
        canvas.drawInlineImage(logo_path, doc.leftMargin, doc.height + doc.topMargin - 0, width=25, height=25)

        # Draw the footer
        page_num = canvas.getPageNumber()
        text = "Page %s" % page_num
        canvas.drawString(doc.leftMargin, inch / 2, "Bearden Data Solutions LLC")
        canvas.drawRightString(doc.width + doc.leftMargin, inch / 2, text)


if __name__ == '__main__':
    response = lambda_handler(
        {"body": {"report_type": "stock_analysis", "send_email": True, }},
        {})
    response

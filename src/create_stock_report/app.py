from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import boto3
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
from reportlab.pdfgen import canvas
import time
from tools.alpha_vantage_helper import get_daily_adjusted_processed
from tools.os_helper import delete_files
from tools.pattern_helper import calculate_ichimoku


def lambda_handler(event, context):
    # Parse input
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)

    periods_for_plot = body.get('periods_for_plot', 180)
    send_email = body.get('send_email', False)
    symbol = body.get('symbol', None)

    # Validate input
    if 'report_type' not in body.keys():
        return {
            'statusCode': 400,
            'body': json.dumps(f'Bad Request: Missing required parameter: report_type')
        }
    report_type = body['report_type']

    tmp_files = []

    if (report_type == 'stock_analysis') & isinstance(symbol, str):

        # Create PDF
        pdf_path = "/tmp/report.pdf"
        tmp_files.append(pdf_path)
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 750, "Trading Report")

        # get api keys
        ssm = boto3.client('ssm')
        parameter = ssm.get_parameter(Name='ALPHAVANTAGE_API_KEY', WithDecryption=True)
        alphavantage_api_key = parameter['Parameter']['Value']

        # get technical indicators
        ts = TimeSeries(key=alphavantage_api_key, output_format='pandas')
        data, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize='full')
        data = get_daily_adjusted_processed(data)

        ichimoku_df = calculate_ichimoku(data)

        # Plotting
        # Create a candlestick chart
        # Create a new figure with an Axes object
        ichimoku_df_reduced = ichimoku_df.iloc[-100:]

        ichimoku_lines = [
            ('tenkan_sen', 'blue', 'Tenkan Sen'),
            ('kijun_sen', 'red', 'Kijun Sen'),
            ('senkou_span_a', 'green', None),
            ('senkou_span_b', 'orange', None),
            ('chikou_span', 'purple', 'Chikou Span')
        ]

        # Create the candlestick chart with Ichimoku overlay
        fig, axes = mpf.plot(ichimoku_df_reduced,
                             type='candle',
                             # mav=(9, 26, 52),
                             volume=True,
                             figratio=(14, 7),
                             style='yahoo',
                             returnfig=True  # This returns the figure and axes
                             )

        ax1 = axes[0]  # This is the axis of the main panel

        # Plot Ichimoku lines
        # to align with mplfinancem dates converted to their indices
        dates = list(range(len(ichimoku_df_reduced.index)))
        for line, color, label in ichimoku_lines:
            if label:
                ax1.plot(dates, ichimoku_df_reduced[line], color=color, label=label)
            else:
                ax1.plot(dates, ichimoku_df_reduced[line], color=color)
        ax1.fill_between(dates, ichimoku_df_reduced['senkou_span_a'], ichimoku_df_reduced['senkou_span_b'],
                         where=ichimoku_df_reduced['senkou_span_a'] >= ichimoku_df_reduced['senkou_span_b'],
                         color='lightgreen',
                         zorder=0,
                         # label='Senkou Span A > B'
                         )
        ax1.fill_between(dates, ichimoku_df_reduced['senkou_span_a'], ichimoku_df_reduced['senkou_span_b'],
                         where=ichimoku_df_reduced['senkou_span_a'] < ichimoku_df_reduced['senkou_span_b'],
                         color='lightcoral',
                         zorder=0,
                         # label='Senkou Span A < B'
                         )
        # Create legend
        ax1.legend(loc='best')

        # Set title
        ax1.set_title('Daily Price Candles with Ichimoku Cloud Overlay')

        # Adjust the left margin of the plot
        # plt.subplots_adjust(left=0.05)  # Adjust the value as needed to trim the white space

        # Save the plot to a file
        plot_file_path = "/tmp/ichimoku_plot.png"
        tmp_files.append(plot_file_path)
        plt.savefig(plot_file_path, format='png')  # , bbox_inches='tight')
        plt.show()

        # Draw the plot on the ReportLab canvas
        c.drawImage(plot_file_path, -100, 500, width=700, height=350)
        # Start a new page
        c.showPage()

        ti = TechIndicators(key=alphavantage_api_key, output_format='pandas')
        data, meta_data = ti.get_rsi(symbol=symbol, interval='daily', time_period=14, series_type='close')
        data_reduced = data.iloc[-periods_for_plot:]
        rsi_values = [float(value) for value in data_reduced['RSI']]
        dates = data_reduced.index
        # Create the plot
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
        ax.plot(dates, rsi_values, marker='o')

        # Set the title and labels
        ax.set_title('RSI Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('RSI')

        # Rotate date labels for better readability
        fig.autofmt_xdate()

        # Show the plot
        plt.grid()
        # plt.show()

        # Save the plot to a file
        plot_file_path = "/tmp/plot.png"
        tmp_files.append(plot_file_path)
        plt.savefig(plot_file_path, format='png')

        # Draw the plot on the ReportLab canvas
        c.drawImage(plot_file_path, 50, 500, width=400, height=300)

        # Additional PDF content (e.g., text)
        c.drawString(50, 480, "Sample Plot:")

        c.save()

        if send_email:
            parameter = ssm.get_parameter(Name='FROM_EMAIL', WithDecryption=True)
            from_email = parameter['Parameter']['Value']
            parameter = ssm.get_parameter(Name='TO_EMAILS', WithDecryption=True)

            to_emails = parameter['Parameter']['Value'].split(',')
            for to_email in to_emails:
                # Create MIME message
                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = 'PDF Report'

                # Add text body (optional)
                text = MIMEText('Please find the attached PDF report.', 'plain')
                msg.attach(text)

                # Attach PDF
                with open("/tmp/report.pdf", "rb") as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="report.pdf"')
                msg.attach(part)

                # Send email
                client = boto3.client('ses')
                response = client.send_raw_email(
                    RawMessage={'Data': msg.as_string()},
                    Source=msg['From'],
                    Destinations=[msg['To']]
                )
                time.sleep(1)
            delete_files(tmp_files)
            return {'statusCode': 200, 'body': 'Report sent successfully!'}
        else:
            # delete_files(tmp_files)
            return {'statusCode': 200, 'body': 'Report created successfully, but not sent!'}
    else:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Bad Request: report_type={report_type} is an unknown report type for symbol={symbol}.')
        }


if __name__ == '__main__':
    response = lambda_handler(
        {"body": {"report_type": "stock_analysis", "send_email": True, "symbol": "COE"}},
        {})
    response

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

from market_summary_pdf_gen import  retrieve_csv_summary_data, retrieve_png_files_list, generate_pdf_report, run

# Target Folder is "Log"
def setup_logging(target_folder):
    log_folder = Path(target_folder)
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file = log_folder / 'app.log'

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        encoding='utf-8',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    return logger

# Target folder is "Output"
def setup_todays_directory(target_folder):
    # Create timestamp folder for the day

    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    today_folder = Path(target_folder) / today
    today_folder.mkdir(parents=True, exist_ok=True)

    # Create Chart folder

    chart_folder = today_folder / 'Charts'
    chart_folder.mkdir(parents=True, exist_ok=True)

    # Create Analysis folder
    analysis_folder = today_folder / 'Analysis'
    analysis_folder.mkdir(parents=True, exist_ok=True)


def fetch_data(logger):
    timestamp_filename = pd.Timestamp.now().strftime('%Y-%m-%d')
    data_file = Path('Data') / f'{timestamp_filename}.csv'
    if not data_file.exists():
        logger.error(f"Data file {data_file} does not exist.")
        raise FileNotFoundError(f"Data file {data_file} does not exist.")
    return pd.read_csv(data_file)


def calculate_statistics(df):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

    daily_returns = np.log(df['Close'] / df['Close'].shift(1))
    valid_returns = daily_returns.dropna()

    summary = pd.DataFrame([{
        'Mean Return': valid_returns.mean(),
        'Standard Deviation': valid_returns.std(),
        'Annualized Volatility': valid_returns.std() * np.sqrt(252),
        'Max Gain': valid_returns.max(),
        'Max Loss': valid_returns.min(),
    }])

    series = pd.DataFrame({
        'Date': df['Date'],
        'Daily Returns': daily_returns,
        '5-Period Moving Average': df['Close'].rolling(window=5, min_periods=5).mean(),
        '5-Period Rolling Volatility': daily_returns.rolling(window=5, min_periods=5).std(),
    })

    return {'summary': summary, 'series': series}

#Target folder is "Output"
def upload_statistics(statistics_data, target_folder):
    timestamp_filename = pd.Timestamp.now().strftime('%Y-%m-%d')
    output_file = Path(target_folder) / timestamp_filename / 'Analysis' / f'statistics_{timestamp_filename}.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    summary = statistics_data['summary'].iloc[0]
    columns = ['Record Type', 'Date', 'Mean Return', 'Standard Deviation', 'Annualized Volatility', 'Max Gain', 'Max Loss', 'Daily Returns', '5-Period Moving Average', '5-Period Rolling Volatility']

    summary_row = pd.DataFrame([{
        'Record Type': 'Summary',
        'Date': pd.NaT,
        'Mean Return': summary['Mean Return'],
        'Standard Deviation': summary['Standard Deviation'],
        'Annualized Volatility': summary['Annualized Volatility'],
        'Max Gain': summary['Max Gain'],
        'Max Loss': summary['Max Loss'],
        'Daily Returns': pd.NA,
        '5-Period Moving Average': pd.NA,
        '5-Period Rolling Volatility': pd.NA,
    }]).reindex(columns=columns)

    series_export = statistics_data['series'].copy()
    series_export.insert(0, 'Record Type', 'Series')
    for col in ['Mean Return', 'Standard Deviation', 'Annualized Volatility', 'Max Gain', 'Max Loss']:
        series_export[col] = pd.NA
    series_export = series_export.reindex(columns=columns)

    pd.concat([summary_row, series_export], ignore_index=True).to_csv(output_file, index=False)


# Target folder is "Output"
def generate_charts_png(df, statistics_df,target_folder):
    timestamp_filename = pd.Timestamp.now().strftime('%Y-%m-%d')
    chart_folder = Path(target_folder) / timestamp_filename / 'Charts'
    chart_folder.mkdir(parents=True, exist_ok=True)

    x_dates = pd.to_datetime(statistics_df['Date']).tolist()
    closing_prices = pd.to_numeric(df['Close'], errors='coerce').tolist()

    # Plot Closing Price
    plt.figure(figsize=(10, 6))
    plt.plot(x_dates, closing_prices, label='Closing Price', color='blue')
    plt.plot(x_dates, statistics_df['5-Period Moving Average'].tolist(), label='5-Period Moving Average', color='orange')
    plt.title('Closing Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_folder / f'closing_price_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot Daily Returns
    plt.figure(figsize=(10, 6))
    plt.plot(x_dates, statistics_df['Daily Returns'].tolist(), label='Daily Returns', color='green')
    plt.title('Daily Returns Over Time')
    plt.xlabel('Date')
    plt.ylabel('Daily Returns')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_folder / f'daily_returns_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot Rolling Volatility
    plt.figure(figsize=(10, 6))
    plt.plot(x_dates, statistics_df['5-Period Rolling Volatility'].tolist(), label='5-Period Rolling Volatility', color='red')
    plt.title('5-Period Rolling Volatility Over Time')
    plt.xlabel('Date')
    plt.ylabel('Rolling Volatility')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_folder / f'rolling_volatility_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot Histogram of Daily Returns
    plt.figure(figsize=(10, 6))
    plt.hist(statistics_df['Daily Returns'].dropna(), bins=50, color='purple', alpha=0.7)
    plt.title('Histogram of Daily Returns')
    plt.xlabel('Daily Returns')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(chart_folder / f'histogram_daily_returns_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot Histogram of 5-Period Rolling Volatility
    plt.figure(figsize=(10, 6))
    plt.hist(statistics_df['5-Period Rolling Volatility'].dropna(), bins=50, color='brown', alpha=0.7)
    plt.title('Histogram of 5-Period Rolling Volatility')
    plt.xlabel('5-Period Rolling Volatility')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(chart_folder / f'histogram_rolling_volatility_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot Boxplot of Daily Returns
    plt.figure(figsize=(10, 6))
    plt.boxplot(statistics_df['Daily Returns'].dropna(), orientation='horizontal')
    plt.title('Boxplot of Daily Returns')
    plt.xlabel('Daily Returns')
    plt.tight_layout()
    plt.savefig(chart_folder / f'boxplot_daily_returns_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot Boxplot of 5-Period Rolling Volatility
    plt.figure(figsize=(10, 6))
    plt.boxplot(statistics_df['5-Period Rolling Volatility'].dropna(), orientation='horizontal')
    plt.title('Boxplot of 5-Period Rolling Volatility')
    plt.xlabel('5-Period Rolling Volatility')
    plt.tight_layout()
    plt.savefig(chart_folder / f'boxplot_rolling_volatility_{timestamp_filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

    
    
def Run(target_folder='Output', log_folder='Log'):
    logger = setup_logging(log_folder)
    setup_todays_directory(target_folder)
    df = fetch_data(logger)
    statistics_data = calculate_statistics(df)
    upload_statistics(statistics_data, target_folder)
    generate_charts_png(df, statistics_data['series'], target_folder)
    logger.info("Market summary tool completed successfully.")
    run(target_folder, log_folder)

Run()
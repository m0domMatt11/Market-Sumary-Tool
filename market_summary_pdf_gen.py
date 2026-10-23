import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

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
def retrieve_csv_summary_data(target_folder):
    timestamp_filename = pd.Timestamp.now().strftime('%Y-%m-%d')
    data_file = Path(target_folder) / timestamp_filename / 'Analysis' / f'statistics_{timestamp_filename}.csv'
    if not data_file.exists():
        raise FileNotFoundError(f"Data file {data_file} does not exist.")
    df = pd.read_csv(data_file)
    mean_return = df['Mean Return'].values[0]
    std_dev = df['Standard Deviation'].values[0]
    annualized_volatility = df['Annualized Volatility'].values[0]
    return mean_return, std_dev, annualized_volatility

# target folder is "Output"
def retrieve_png_files_list(target_folder):
    timestamp_filename = pd.Timestamp.now().strftime('%Y-%m-%d')
    chart_folder = Path(target_folder) / timestamp_filename / 'Charts'
    if not chart_folder.exists():
        raise FileNotFoundError(f"Chart folder {chart_folder} does not exist.")
    png_files = list(chart_folder.glob('*.png'))
    return png_files

def generate_customer_paragraph(mean_return, std_dev,  annualized_volatility):
    if annualized_volatility > 0.2:
        annualized_statement = "The market is highly volatile."
    elif annualized_volatility > 0.1:
        annualized_statement = "The market is moderately volatile."
    else:
        annualized_statement = "The market is relatively stable."

    if mean_return > 0.02:
        return_statement = "Overall, the market has shown positive returns."
    elif mean_return < -0.02:
        return_statement = "Overall, the market has shown negative returns."
    else:
        return_statement = "Overall, the market has shown no significant returns."

    paragraph_text = f""" On {pd.Timestamp.now().strftime('%Y-%m-%d')}, the mean return was {mean_return:.4f}, the standard deviation was {std_dev:.4f}. {annualized_statement} {return_statement} """

    return paragraph_text

def generate_pdf_report(target_folder, mean_return, std_dev, annualized_volatility, png_files):
    timestamp_filename = pd.Timestamp.now().strftime('%Y-%m-%d')
    pdf_file_path = Path(target_folder) / timestamp_filename / f'market_summary_{timestamp_filename}.pdf'
    doc = SimpleDocTemplate(str(pdf_file_path))
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,          # Must scale up with fontSize to avoid overlaps
        alignment=TA_CENTER,
        spaceAfter=12        # Native space tracking below the paragraph
    )

    body_style = ParagraphStyle(
        'BodyJustified',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        alignment=TA_JUSTIFY
    )

    # Add title
    story.append(Paragraph("Market Summary Report", title_style))

    # Add summary paragraph
    summary_paragraph = generate_customer_paragraph(mean_return, std_dev, annualized_volatility)
    story.append(Paragraph(summary_paragraph, body_style))

    # Add charts
    for png_file in png_files:
        story.append(Spacer(1, 12))
        story.append(Image(str(png_file), width=400, height=300))

    doc.build(story)

    
def run(target_folder = "Output", logging_file = "Log"):
    logger = setup_logging(logging_file)
    mean_return, std_dev, annualized_volatility = retrieve_csv_summary_data(target_folder)
    png_files = retrieve_png_files_list(target_folder)
    generate_pdf_report(target_folder, mean_return, std_dev, annualized_volatility, png_files)


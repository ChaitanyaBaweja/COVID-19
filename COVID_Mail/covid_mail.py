# -*- coding: utf-8 -*-
"""
Last Updated Thu 19 Mar, 2020

@author: Chaitanya Baweja
"""

# Scraping library
from selenium import webdriver

# Mail Libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Table Library
from tabulate import tabulate

# for scheduling
import schedule
import time

# take input initially and setup driver once
Country = input() 
driver = webdriver.Chrome('path/to/chromedriver')

def extract_data(Country_name):
    
    # reloading data
    driver.get('https://www.worldometers.info/coronavirus/')
    time.sleep(2) # for giving some time to load
    
    # getting table out
    table = driver.find_element_by_xpath('//*[@id="main_table_countries_today"]/tbody[1]')
    
    # getting country row out
    xpath = "//td[contains(text(), '%s')]"% Country_name
    
    # There are some countries whose names are in reference links
    # Those will go to except statement
    try:
        country_element = table.find_element_by_xpath(xpath)
        row = country_element.find_element_by_xpath("./..")
    except:
        country_element = table.find_element_by_link_text(Country_name)
        row = country_element.find_element_by_xpath("../..")

    # extracting data from each row_cell
    col_data = row.find_elements_by_tag_name("td")
    data_val = [x.text for x in col_data]

    # converting data into a dictionary and then a table
    data_keys = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths','Active Cases','Total Recovered','Serious, critical cases','Total Cases per million']
    data_dict = dict(zip(data_keys,data_val))
    
    return data_dict

def send_mail(data_dict):
    # setting mail up
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    # setting login details
    server.login('email_addr', 'email_pass')
    
    # mail subject
    subject = 'COVID-19 stats for your country'
    
    # mail body
    text = """Data regarding COVID-19 in your country today. Source: https://www.worldometers.info/coronavirus/ 
    
    {table}

    Regards,

    Covid-update"""
    
    # mail html
    html = """
    <html>
    <head>
    <style> 
      table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
      th, td {{ padding: 5px; }}
    </style>
    </head>
    <body><p>Data regarding COVID-19 in your country today. Source: 
    <a href="https://www.worldometers.info/coronavirus/">Worldometers</a>
    </p>
    {table}
    <p>Regards,</p>
    <p>Covid-update</p>
    </body></html>
    """
    
    text = text.format(table=tabulate(data_dict.items(), tablefmt="grid"))
    html = html.format(table=tabulate(data_dict.items(), tablefmt="html"))
    
    message = MIMEMultipart(
        "alternative", None, [MIMEText(text), MIMEText(html,'html')])

    message['Subject'] = subject
    message['From'] = 'sender_mail' # sender
    message['To'] = 'receiver_mail' # receiver

    
    server.sendmail(
        message['From'],
        message['To'],
        message.as_string()
    )
    print('Hey Email has been sent!')

    server.quit()

def covid_update():
    data_dict = extract_data(Country) # extract fresh data
    send_mail(data_dict) # sending email based on the dict
    return

# scheduled for every day at 10:00 am
schedule.every().day.at("10:00").do(covid_update)

while True:
    schedule.run_pending()
    time.sleep(1) # wait one minute
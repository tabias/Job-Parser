import itertools

import pandas as pd

from urllib import robotparser
from urllib import request as u
from sys import exit

from bs4 import BeautifulSoup

# The Required dictionaries to be used later on in the script.
Dict, profile, profile_company = {}, {}, {}
# Lists
location_list = []
company_list = []
job_title = []
job_urls = []
date_list = []

def allow():

    '''
    The purpose of this module will be to go to the robots.txt file and ask for access for  the parsing process
    to begin. If the robot.txt denies the required access, then the program will be halted and a message will be
    displayed explaining that we do not have the rights to parse the site.
    '''

    rp = robotparser.RobotFileParser()
    rp.set_url("http://be.indeed.com/robots.txt")
    rp.read()
    access = rp.can_fetch("*","http://be.indeed.com/jobs?q=python%20analyst&l=CA" )
    return access


class Parser:
    def __init__(self):
        self.df = pd.DataFrame([])
        self.url = ''
        self.jobstats = pd.DataFrame([])
        self.textdata = pd.DataFrame([])

    def pull_job_all(self, job, region='2220', radius=30, date=True):
        '''

        :param job:
        :param region:
        :param radius:
        :param date:
        :return:
        '''
        jobstats = self.jobstats
        textdata = self.textdata
        # fetch the number of jobs
        soup = self.pull_job(job, region, radius, date)
        jobstats = jobstats.append(self.data_parse(soup, job))
        textdata = textdata.append(self.list_jobs(soup, job))
        for text in soup.find_all("div", id="searchCount"):
            count = str(text.get_text()).split(' ')[-1] #strip only the last number so we know the total count
        stop = int(count)//10
        print('found {count} jobs for {job}'.format(job=job, count=count))
        for page in range(10, stop*10, 10):
            soup = self.pull_job(job, region, radius, date, page=page)
            jobstats = jobstats.append(self.data_parse(soup, job), ignore_index=True)
            #print(jobstats)
            textdata = textdata.append(self.list_jobs(soup, job), ignore_index=True)
        return jobstats, textdata

    def pull_job(self, job, region='2220', radius=30, date=True, page=0):
        '''

        :param job: the job query we are searching
        :param region: the region (postal code preferably we want Default = 2220
        :param radius: what range we want to search for (km's) Default = 30
        :param date: (bool) sorted according to date Default = True3
        :param all: (bool) fetch them all Default = False
        :return: return the soup for data parse
        '''

        #first check if we can actually access it
        if not allow():
            exit('Robot not allowed, quitting')

        # check if we listed a job, else raise error
        if not job:
            raise ValueError('need a job')

        # base url setting
        url = "http://be.indeed.com/jobs?q="+ str(job).replace(' ','%2B') \
                   + "&l="+ str(region) \
                   + "&radius=" + str(radius) \
                   + "&fromage=last"
        if date:
            url += '&sort=date'
        if page:
            url += '&start='+str(page)

        response = u.urlopen(url)
        response = response.read()
        soup = BeautifulSoup(response, "html.parser")
        #print(url)
        #print(soup.prettify())

        return soup

    def data_parse(self, soup, job):
        '''

        :param x: x is the boolean parameter that is passed from the previous query with the robots.txt file./
         Once passed        then the first process will be to validate the required access, displaying a message/
            if it does not agree.
        :param job: (str) a list of jobs will be passed to determine which one has the most amount of jobs possible.
        :param soup: bs4 object
        :return: The process will return a Pandas DataFrame table that displays the quantity of jobs available/
         per query. For instance, Python engineer- 10,000 jobs available, Python Analyst- 5000 jobs e.t.c.

        '''



        # Once access is granted then the process starts parsing the data by first comparing the number/
        # of jobs available and returning the facts and figures.
        for text in soup.find_all("div", id="searchCount"):
            data = str(text.get_text()).split(' ')[-1] #strip only the last number so we know the total count
            job2 = job.replace("+", " ")

        return [job2, data]

    def list_jobs(self, soup, job):

        for post in soup.find_all("div", {"class":"  row  result"}):
            # job title
            jobs = post.find_all("a", {"class": "turnstileLink"})
            job_contents = (job.get_text(' ', strip=True)[:25] for job in jobs)
            job_url = ('http://be.indeed.com'+job['href'] for job in jobs if job['href'])

            job_urls.append(job_url)
            job_title.append(job_contents)
            #           company Name
            companies = post.find_all("span", {"itemprop":"name"})
            company_content = (company.get_text(' ', strip=True)[:20] for company in companies)
            company_list.append(company_content)
            #           location
            locations = post.find_all("span", {"itemprop":"addressLocality"})
            locality = (location.get_text(' ', strip=True)[:15] for location in locations)
            location_list.append(locality)
            # posting dat
            dates = post.find_all("span", {"class":"date"})
            date = (date.get_text(' ', strip=True).split(' ')[0] for date in dates)
            date_list.append(date)
        # return location_list
        profile["Job Title"] =(list(itertools.chain.from_iterable(job_title)))
        profile["Location"] = (list(itertools.chain.from_iterable(location_list)))
        profile_company["Company"] = (list(itertools.chain.from_iterable(company_list)))
        profile_company["Date"] = (list(itertools.chain.from_iterable(date_list)))
        profile_company["url"] = (list(itertools.chain.from_iterable(job_urls)))

        # Turning the list into a panda DataFrame which will have 3 columns. These columns/
        # include jobtitle, job location, and Company
        df3 = pd.DataFrame(profile_company)
        df4 = pd.DataFrame(profile).join(df3, how='left')
        return df4




# main module that manages all the other modules in the  script
def main(jobs):

    username = "tabias@gmail.com" #input("please enter your Plotly Username: \n")
    api_key = "2j3vo9xtbh" #input("please enter your Plotly Api Key: \n")
    local = "2220"
    radius = "35"
    for job in jobs:
            # Declaring the classes that have been used sequentially
            parser = Parser()
            #salary = SalaryEstimates()

            # functions that are present in these classes respectively
            #soup = parser.pull_job(job)
            #items = parser.data_parse(soup, job)

            items, final = parser.pull_job_all( job, region=local, radius=radius, date=True)
            #write final to csv


            final.to_excel(job+'.xlsx',index=False)

            #final = parser.list_jobs(soup, job)
            print("-~"*50)
            print("-~"*50)
            print("the requested job was", job)
            print("-~"*50)
            print(final)
            print("-~"*50)
            print("-~"*50)
            # we don't have a salary posting so can't use it
            #print("the requested job salary was "+job+" salary")
            #print("-~"*50)
            #wage_compiled = salary.salary_parser(soup)
    #print("\n")
    #print("-~"*50)
    #print("-~"*50)
    #print("The total number of jobs in each field is")
    #print("-~"*50)
    #print(items)
    # compares the total number of jobs visually on Plotly
    #parser.graph_parsed_data(username, api_key)

    # runs the salary graph on Plotly
    #salary.graphing_salary(username, api_key)

main(["process engineer",'maintenance engineer', 'project engineer', 'proces ingenieur'])
#main(["proces ingenieur"])
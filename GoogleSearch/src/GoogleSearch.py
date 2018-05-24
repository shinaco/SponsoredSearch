# -*- coding: utf-8 -*-
import datetime
import errno
import glob
import json
import logging
import os
import random
import re
import requests
import signal
import shlex
import subprocess
import urllib
from   bs4 import BeautifulSoup
from   argparse import ArgumentParser
from   functools import wraps
from   subprocess import call
from   time import sleep
from   web2screenshot import make_screenshot
from   DataSource import SearchDB


#********************* Global Vars *************************
MAX_VPN_ATTEMPTS = 5
#***********************************************************

scriptdir = os.path.dirname(os.path.realpath(__file__))
parentdir = scriptdir.replace("src","")

# create logger
logger = logging.getLogger('GoogleSearchLogger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
fh = logging.FileHandler('../logs/google_search_{:%Y%m%d}.log'.format(datetime.datetime.now()))
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(fh)
logger.addHandler(ch)

# 'application' code
logger.info('Script Directory' + scriptdir)
logger.info('Parent Directory' + parentdir)
cols = [
        "City",
        "State",
        "Datetime",
        "Search term",
        "Google URL",
        "Ad URL Website",
        "Website Name",
        "Vendor",
        "Position Num",
        "Position",
        "Result is consistent",
        "Page number",
        "Type of result",
        "Comments",
        "Ad Value",
        "Static File Path"]

# the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,
# netscape for more user agent strings,you can find it in
# http://www.useragentstring.com/pages/useragentstring.php

user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"\
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",\
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",\
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",\
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",\
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",\
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]

def timeout(seconds,error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum,frame):
            raise Exception(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM,_handle_timeout)
            signal.setitimer(signal.ITIMER_REAL,seconds)
            try: result = func(*args,**kwargs)
            finally: signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

# Organic result class


class organic:
    def __init__(self, name, pagenum = 1):
        self.product_name = name
        self.type         = "organic"
        self.pagenum      = pagenum

    def to_string(self):
        msg  = self.type + " Product Name   : %s\n"   % self.product_name
        msg += self.type + " Product URL    : %s\n"   % self.product_url
        msg += self.type + " Product Price  : %s\n"   % self.price
        msg += self.type + " Product Vendor : %s\n"   % self.vendor
        msg += self.type + " file location  : %s\n\n" % self.filename
        return msg


    def get_random_filename(self):
        vendor  = re.sub('[^0-9a-zA-Z]+', '_', self.vendor)
        product = re.sub('[^0-9a-zA-Z]+', '_', self.product_name)
        self.filename = "../data/" + self.type + product[:15] + vendor + str(random.randint(1, 100000)) + ".png"
        self.filename = os.path.abspath(self.filename)
        self.htmlfn   = self.filename.replace("png", "html")

    def convert_url_to_pdf(self):
        self.get_random_filename()
        try:
            if "http" not in self.product_url:
                www = re.compile("(w{3,})")
                if(www.match(self.product_url)):
                    self.product_url = "http://" + self.product_url
                else:
                    logger.debug("Can't find http in URL : please check.\nURL %s\n", self.product_url)
                    self.filename = "NA"
                    return
            make_screenshot(self.product_url, self.filename)
            self.processPDF = True
        except Exception as e:
            logger.exception("message")
            self.filename = "NA"
            self.processPDF = False

        # Save html as well.
        try:
            request = urllib.request.Request(self.product_url, None, {'User-Agent': random.choice(user_agent_list)})
            urlfile = urllib.request.urlopen(request, timeout=10)
            htmlcon = urlfile.read()
            with open(self.htmlfn, "w") as text_file:
                print(f"{htmlcon}", file=text_file)
            self.processHTML = True
        except Exception as e:
            logger.exception("message")
            self.htmlfn = "NA"
            self.processHTML = False


# Advertisement class
class advertiz(organic):
    def __init__(self, name, pagenum = 1):
        self.product_name = name
        self.type         = "SponsoredAd"
        self.pagenum      = pagenum

class SearchResult:
    def __init__(self, keyword, screenshot = True):
        self.keyword    = urllib.parse.quote_plus(keyword)
        self.screenshot = screenshot
        self.user       = self.process_request()
        self.ads        = []
        self.address    = None
        self.soup       = None
        self.city       = None
        self.state      = None
        self.ads        = []


    def create_request(self, pagenum, num = 10, start = 0):
        self.address = "http://www.google.com/search?q=%s&num=%d&hl=en&start=%d" % (self.keyword, num, start)
        self.request = urllib.request.Request(self.address, None, {'User-Agent': self.user})
        self.pagenum = pagenum

    def process_request(self):
        ua = random.choice(user_agent_list)
        return ua

    def get_google_search_result(self):
        self.urlfile = urllib.request.urlopen(self.request)
        self.page    = self.urlfile.read().decode('utf-8')
        self.save_html(self.page, prefix="GoogleSearch")
        self.soup    = BeautifulSoup(self.page, 'html.parser')
        self.get_location()

    def get_location(self):
        try:
          url          = 'http://freegeoip.net/json'
          r            = requests.get(url)
          j            = json.loads(r.text)
          logger.info("Trying to get location : {} ".format(j))
          self.city    = j['city']
          self.state   = j['region_code']
          self.processLocation = True
        except Exception as e:
          logger.info("Can't reach FREEGEOIP")
          logger.info(e)
          self.processLocation = False
	  
	
    def to_string(self):
        print("Keyword : %s" % self.keyword)
        if self.address:
            print("Address : %s" % self.address)
        if self.soup:
            print("Title   : %s" % self.soup.title.string)
        if self.city:
            print("City    : %s" % self.city)
        if self.state:
            print("State   : %s" % self.state)
        if self.ads:
            print("Total search results: {}".format(len(self.ads)))

    def parse_ads(self):
        # # get right ads
        self.parse_right_ads()
        # #parse right tables
        self.parse_right_ads_table()
        # #parse right tile
        self.parse_right_tile()
        #get top sponsored
        self.parse_top_sponsored()
        # # get top ads
        self.parse_top_ads()
        #get_organic_results
        self.parse_organic_results()
        # #get bottom ads
        self.parse_bottom_ads()

    # todo - all the ads
    def parse_top_sponsored(self):
        try:
            self.top_panel_ads = self.soup.find(id="tvcap")
            self.top_sponsored  = self.top_panel_ads.find_all("li", {"class" : "ads-ad"})
            logger.info("Found {} ads on top organic panel".format(len(self.top_sponsored)))
            for item in self.top_sponsored:
                item_name = item.find('a', class_ = re.compile('^V0MxL')).text
                logger.info("Item name : {}".format(item_name))
                ad = advertiz(item_name, self.pagenum)
                ad.location = "top sponsored"
                ad.product_url = item.find('a', class_ = re.compile('^V0MxL'))['href']
                if (ad.product_url is None):
                    continue
                ad.price = ""
                ad.vendor = self.get_vendor_from_organic(ad.product_url)
                ad.convert_url_to_pdf()
                self.ads.append(ad)
            self.processedSponsoredTop = True
        except Exception as e:
            logger.info("Unable to parse top sponsored Links")
            if(self.top_sponsored is not None):
                logger.debug(self.top_sponsored)
            logger.debug(e)
            self.processedSponsoredTop = False
    def parse_right_ads_table(self):
        root_class_name = "twpSFc mnr-c"
        price_ex = re.compile(r"(\$\d+[\.\d]+)\b")
        logger.info("Parsing right side tables")
        try:
            self.right_ads_table_data = self.soup.find_all('div', {"class": root_class_name})
            logger.info("Found {} ads on the right hand table".format(len(self.right_ads_table_data)))
            for table_ad in self.right_ads_table_data:
                data_table = table_ad.find("table", {"class" : "ts"})
                if data_table is not None:
                    logger.debug("Table not found.. check the table class name")
                    cells = data_table.find_all("td")
                    print(cells)
                    try:
                        ad_data = cells[1].find('span', {"class":"pymv4e"}).text
                        print(ad_data)
                        ad = advertiz(ad_data, self.pagenum)
                        ad.location = "RHS Table"
                        ad_urls = cells[1].find_all("a", href=True)
                        logger.info("Found {} URLS".format(len(ad_urls)))
                        for url in ad_urls:
                            logger.debug(url)
                            logger.debug("://" in url['href'])
                            if "://" in url['href']: 
                                ad.product_url = url['href']
                        if ad.product_url is None:
                            ad.product_url = "NA"
                            continue
                        logger.info(ad.product_url)
                        if(price_ex.search(str(cells[1]))):
                            ad.price = price_ex.search(str(cells[1])).group(1)
                        ad.vendor = str(cells[1].find("div", {"class" : "Ndt4Qb", "text" : True}))
                        ad.convert_url_to_pdf()
                        self.ads.append(ad)
                    except Exception as e:
                        logger.debug(e)
        except:
            logger.debug("Right table Ads: If there are tables in the original html - maybe the class-id in the corresponding block is not correct.")

    def parse_right_ads(self):
        try:
            self.right_ads = self.soup.find(id="rhs")
            ad_data = self.right_ads.find_all('div' , {"class" : re.compile("jackpot-title-ratings-container.*?")})[0]
            self.right_ad_list = self.right_ads.find_all('div' , {"class": "gkMlQe"})
            logger.info("Found {} ads on the right hand side".format(len(self.right_ad_list)))
            for item in self.right_ad_list:
                # create ad object
                try:
                    ad                = advertiz(ad_data.get_text(), self.pagenum)
                    ad.location       = "RHS"
                    ad.product_url    = item.find('a', {"class":"plantl"})
                    if (ad.product_url is None):
                        continue
                    ad.product_url    = ad.product_url['href']
                    logger.info(ad.product_url)
                    logger.info(item.find('a', {"class":"plantl"})['id'])
                    ad.price          = item.find('span', {"class": "rgc6j"}).text
                    ad.vendor         = self.get_vendor_from_organic(ad.product_url)
                    ad.convert_url_to_pdf()
                    self.ads.append(ad)
                except Exception as e:
                    logger.debug("Unable to parse some ads on the right.")
            self.processRightAd = True
        except Exception as e:
            logger.info("Unable to parse right_ads\n")
            logger.debug(e)
            self.processRightAd = False

    def parse_top_ads(self):
        try:
            self.top_ads = self.soup.find("div", {"id": "taw"})
            self.top_ads_list = self.top_ads.find_all(class_="mnr-c pla-unit")
        except Exception as e:
            logger.info("Unable to parse top_ads\n")
            if(self.top_ads is not None):
                logger.debug(self.top_ads.prettify())
            logger.debug(e)
            self.processTopAd = False
            return

        for item in self.top_ads_list:
            try:
                ad_data        = item.find('a', {"class" : "plantl pla-unit-title-link"})
                # create ad object
                ad             = advertiz(ad_data.span.text, self.pagenum)
                ad.location    = "top"
                ad.product_url = ad_data['href']
                ad.price       = item(text=re.compile(r"(\$\d+[\.\d]+)\b"))[0]
                ad.vendor      = item.find(class_="LbUacb").span.get_text()
                ad.convert_url_to_pdf()
                logger.debug(ad.to_string())
                self.ads.append(ad)
            except Exception as e:
                logger.debug(e)
        self.processTopAd = True
    def parse_right_tile(self):
        try:
            self.right_tile = self.soup.find("div", {"class": "rhs_block"})
            self.right_tile_list = self.right_tile.find_all(class_="mnr-c pla-unit")
        except Exception as e:
            logger.info("Unable to parse right_tile\n")
            if(self.right_tile is not None):
                logger.debug(self.right_tile.prettify())
            logger.debug(e)
            self.processRightTileAd = False
            return

        for item in self.right_tile_list:
            try:
                ad_data        = item.find('a', {"class" : "plantl pla-unit-title-link"})
                # create ad object
                ad             = advertiz(ad_data.span.text, self.pagenum)
                ad.location    = "right tile"
                ad.product_url = ad_data['href']
                ad.price       = item(text=re.compile(r"(\$\d+[\.\d]+)\b"))[0]
                ad.vendor      = item.find(class_="LbUacb").span.get_text()
                ad.convert_url_to_pdf()
                logger.debug(ad.to_string())
                self.ads.append(ad)
            except Exception as e:
                logger.debug(e)
        self.processRightTileAd = True
    def parse_bottom_ads(self):
        try:
            self.bottom_ads      = self.soup.find("div", {"id": "bottomads"})
            self.bottom_ads_list = self.bottom_ads.find_all('li' , {"class":"ads-ad"})
            for item in self.bottom_ads_list:
                item_name = item.find('a', class_ = re.compile('^V0MxL')).text
                logger.info("Item name : {}".format(item_name))
                ad = advertiz(item_name, self.pagenum)
                ad.location = "bottom sponsored"
                ad.product_url = item.find('a', class_ = re.compile('^V0MxL'))['href']
                if (ad.product_url is None):
                    continue
                ad.price = ""
                ad.vendor = self.get_vendor_from_organic(ad.product_url)
                ad.convert_url_to_pdf()
                self.ads.append(ad)
            self.processBottomAd = True
        except Exception as e:
            logger.info("Unable to parse bottom_ads\n")
            self.processBottomAd = False

    def parse_organic_results(self):
        try:
            self.organic_list = self.soup.find_all('div', {"class": "g"})
            logger.info("Found {} organic ads".format(len(self.organic_list)))
            count = 1
            for item in self.organic_list:
                try:
                    item_data           = item.find('h3', {"class":"r"}).find('a')
                    item_name           = item_data.text
                    oresult             = organic(item_name, self.pagenum)
                    oresult.product_url = item_data['href']
                    logger.debug("Got url " + item_data['href'])
                    oresult.vendor = self.get_vendor_from_organic(item_data['href'])
                    logger.debug("Got vendor " + oresult.vendor)
                    oresult.location = "organic :" + str(count)
                    logger.debug("Found Organic result item : %d", count)
                    count = count + 1
                    oresult.price = self.get_price_from_organic(item)
                    oresult.convert_url_to_pdf()
                    logger.debug(oresult.to_string())
                    self.ads.append(oresult)
                except Exception as e:
                    logger.info("Can't process organic item at {}, probably a list of images here.".format(count))
                    continue
                self.processOrganic = True
        except Exception as e:
            logger.info("Error while parsing organic result\n")

    def convert_to_csv(self):
      try:
        db = SearchDB("searchresults")
        for ad in self.ads:
            l = self.get_spreadsheet_row(ad)
            print(l)
            db.add_row(self.get_spreadsheet_row(ad))

      except Exception as e:
        logger.debug("Unable to write data to the database.")
        print(e)

    def get_vendor_from_organic(self, text):
        vendor_ex = re.compile(r"http[s]?\W+w{0,3}[\.]?(.*?)\.")
        vendor = vendor_ex.search(text)
        logger.debug("Vendor text : " + text)
        if vendor is None:
            return text
        return vendor.group(1)

    def get_price_from_organic(self, item):
        price_ex = re.compile(r"(\$\d+[\.\d]+)\b")
        try:
            text_to_search = item.find('div', {"class":"slp f"}).text
            print(text_to_search)
            price    = price_ex.search(text_to_search)
        except:
            logger.debug("Unable to find price")
            price = None
        if price is None:
            return "NA"
        else:
            return price.group(1)

    def get_spreadsheet_row(self, ad):
      row = [self.city, self.state, datetime.datetime.now(), self.keyword, \
             self.address, ad.product_url, ad.vendor, "NA", "NA", ad.location, \
             "NA", ad.pagenum, ad.type, "NA", ad.price, "file://"+ad.filename]
      return row

    def save_html(self, data, prefix = "p"):
        filename = "../data/" + prefix + "_" + self.keyword + "_" + str(self.pagenum) + ".html"
        filename = os.path.abspath(filename)
        try:
            with open(filename, "w") as text_file:
                print(f"{data}", file=text_file)
            logger.info("Saved Google Search HTML to : {}".format(filename))
        except Exception as e:
            logger.info("Unable to save google search HTML file")
            logger.debug("Unable to save google search HTML file")
            logger.debug(e)

def main():

    # add command line options
    parser = ArgumentParser(description="Search for Products on Google")
    parser.add_argument("-p", "--product_name", action="store", type=str, help="Enter the product you want to search")
    parser.add_argument("-m", "--screenshot", action="store_true", default = True, help="Do you want to take screenshot")
    parser.add_argument("-n", "--pages", action="store", default = 2, dest = "pages", help="Number of pages to parse")
    # parser.add_argument("-h", "--html", action="store", default=2, dest="html", help="Number of pages to parse")
    args = parser.parse_args()

    report = []
    products = []
    if(args.product_name is not None and args.product_name.strip() != ""):
        logger.info("Got Product Via command line")
        logger.info("Searching for product : {0}".format(args.product_name))
        products.append(args.product_name)
    else:
        logger.info("Running for all products in the database")
        products = get_product_list()
        logger.info("Got {} products to process".format(len(products)))

    for i,product in enumerate(products):
        proc = None
        attempts = 0
        success = 0
        while success != 1 and attempts < MAX_VPN_ATTEMPTS:
            attempts += 1
            logger.debug("Attempt {}".format(attempts))
            try:
                proc = create_vpn()
                logger.info("Processing Product {0} of {1}".format(i + 1, len(products)))
                ad_result = SearchResult(product)
                process_product(ad_result, args.pages)
                logger.debug(ad_result.to_string())
                success = 1
                sleep(5)
            except Exception as e:
                logger.info("Parsing/VPN Issue for {0} in Attempt {1}".format(product, attempts))
                logger.debug(str(e))
            finally:
                kill_vpn(proc)
                if(attempts == MAX_VPN_ATTEMPTS):
                    logger.info("Parsing for {} failed, please rerun".format(product))
                    report.append("Parsing/VPN Issue, please rerun for Product : {}".format(product))
                sleep(10)

    save_results_to_spreadsheet()
    print("***************************** REPORT ************************************")
    print("\n".join(report))
    print("*************************************************************************")

def save_results_to_spreadsheet():
    searchdb = SearchDB("searchresults")
    searchdb.save_to_spreadsheet()

def process_product(searchresult, pages):
    for i in range(pages):
        logger.info("Parsing Page : {}".format(i + 1))
        page_start = i * 10
        searchresult.create_request(pagenum = i + 1, start = page_start)
        searchresult.get_google_search_result()
        searchresult.parse_ads()
        logger.debug(searchresult.to_string())
    searchresult.convert_to_csv()

def get_product_list():
    productdb = SearchDB("products")
    products  = productdb.get_all()
    return [item for item in products['ProductName']]

@timeout(10, "TimedOut while creating VPN")
def create_vpn():
    vpn_dir = parentdir + "vpn/"
    pattern = "us*443.ovpn"
    cfg_file = random.choice(glob.glob(vpn_dir + pattern))
    cmd = "openvpn --redirect-gateway autolocal --config {0} --auth-user-pass {1}".format(cfg_file,
                                                                                          parentdir + "scripts/auth.txt")
    openvpn_cmd = shlex.split(cmd)
    init_vpn = False
    logger.info(" ".join(openvpn_cmd))
    proc = subprocess.Popen(openvpn_cmd, stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)

    linecnt = 0
    while (not init_vpn):
        nextline = proc.stdout.readline()
        if (nextline is None or nextline.strip() == ""):
            linecnt += 1
        elif (nextline.find("Initialization Sequence Completed") != -1):
            init_vpn = True
            logger.info(nextline)
            logger.info("VPN established")
            sleep(2)
        else:
            linecnt += 1
            if (linecnt % 10 == 0):
                logger.debug("waiting..")
                logger.debug(nextline)
    return proc

def kill_vpn(proc):
    logger.debug(proc)
    if proc is not None:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        logger.debug("openvpn killed")
    else:
        logger.debug("openvpn not killed, process not found - killing all openvpn process")
        call(['sudo','killall', 'openvpn'])

if __name__ == "__main__":
    main()

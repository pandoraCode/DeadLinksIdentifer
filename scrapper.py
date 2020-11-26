"""
TP - Scripting Languages - INF8007
Polytechnique Montreal

Students:
    Isabella Ferreira
    Javier Rosales Tovar
    Xiaowei Chen
"""
from __future__ import print_function
from urllib.request import urlparse, urljoin
import os
import ssl
import sys
import getopt
from os import path
from shutil import copyfile
import ntpath
import requests
from bs4 import BeautifulSoup
import select

url_queue = set()
dead_links = set()
url_visited = {}

node_path = "html/"

sys.setrecursionlimit(1500)

# Checks whether url is a valid URL.
def is_valid_link(url: str) -> [bool, bool]:
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc), bool(parsed.scheme)
    except Exception as err:
        eprint(f'Failed to parse url: {err}')
        return bool(0), bool(0)

def parse_html(to_parse: str, is_file: bool, domain_name: str, url: str) -> set:
    links = set()       # distinct links in this url
    try:
        soup = BeautifulSoup(to_parse, 'html.parser')
        tags_contain_href = soup.find_all(href=True)             # Checking for html tags that contain link and text

        if len(tags_contain_href) > 0:
            for tag in tags_contain_href:
                href = tag.attrs.get("href")

                # if href is absolute link
                if href.startswith("http") or href.startswith("https"):
                    href = href
                else:
                    if is_file == 0:        # if it's a website we "build" relative links
                        href = urljoin(url, href)
                    else:                   # if it's a file, we dont know the link
                        href = ""

                parsed_href = urlparse(href)

                # if not in the same domain, skip
                if not parsed_href.netloc == domain_name:
                    continue
                else:       # same domain, valid link
                    if is_valid_link(url=href):
                        links.add(href)
        else:
            print("No tags were identified when parsing the url: ", url)

    except Exception as err:
        eprint("Error occurred during BeautifulSoup parsing:", err)

    return links

# Returns all URLs that are found in a page - no matter if they are dead or not... we check it in the function geturls
def get_links_from(url: str, domain_name: str, is_file: bool) -> set:
    if is_file == 0: # if it's a url, I request the URL and parse the result of the results
        try:        # Requesting website
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}
            r = requests.get(url, headers=headers)
            r.raise_for_status()                    # If the response was successful, no Exception will be raised
        except Exception as err:
            eprint(f'Error occurred during URL Request: {err}')
        else:
            links = parse_html(to_parse=r.text, is_file=0, domain_name=domain_name, url=url)

    elif is_file == 1:           # it's a file
        try:
            with open(url, "r") as html_file:
                contents = html_file.read()
                links = parse_html(to_parse=contents, is_file=1, domain_name=domain_name, url=url)
        except:
            eprint(f'Error occurred during opening file: {err}')
    return links

# Gets all the urls in the page and the urls inside it
def geturls(url: str, domain_name: str, crawl: bool, is_file: bool) -> None:
    print("\n\nGetting URLS... %s \n\n" % (url))
    url_visited[url] = True

    output_file: str = "dead_links_" + domain_name + ".txt"

    if not path.exists("dead_links"):
        os.mkdir("dead_links")

    output_file = "dead_links/"+output_file

    if "localhost" in domain_name:
        # doing this to match same domain in get_links_from function
        domain_name = domain_name.replace("http://", "").replace("https://", "").replace("/", "")
        output_file = "dead_links/"+"dead_links_"+domain_name
    with open(output_file, "a+") as f:
        if (is_file == 0) and (not is_dead_link(link=url)):             # it's a url and not a dead link
            links = get_links_from(url=url, domain_name=domain_name, is_file=is_file)
        elif (is_file == 0) and (is_dead_link(link=url)):               # it's a url and deadlink, add it to the set of dead link and return
            if url not in dead_links:
                dead_links.add(url)
                f.write("%s\n" % (url))
                return
        elif is_file == 1:            # we are parsing a file
            links = get_links_from(url=url, domain_name=domain_name, is_file=is_file)

        if len(links) > 0:
            for link in links:
                if not is_dead_link(link=link):
                    url_queue.add(link)             # Has all valid links
                else:
                    print("It's a dead link\n")
                    if link not in dead_links:
                        dead_links.add(link)
                        f.write("%s\n" % (link))
        else:
            print("No links were found in the website: ", url)

        # Checking sublinks of the links found in the main page
        if crawl == 1:
            try:
                url = url_queue.pop()
                if len(url_queue) == 0:
                    print("\n\n******************* Finished crawling all links and sublinks *******************")
                    print("Number of visited links: ", len(url_visited.keys()))                  # number of visited links
                    print("Number of dead links: ", len(dead_links))                             # number of dead links
                    print("\n\n")
                else:
                    geturls(url=url, domain_name=domain_name, crawl=crawl, is_file=0)           # is_file will always be 0 here because we cannot crawl file
            except Exception as err:
                eprint("Error occurred during popping queue of websites:", err)
        else:
            print("\n\n******************* Finished crawling all links and sublinks *******************")
            print("Number of visited links: ", len(url_visited.keys()))                  # number of visited links
            print("Number of dead links: ", len(dead_links))                             # number of dead links
            print("\n\n")

# if is dead link, return True
def is_dead_link(link: str) -> bool:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}
        r = requests.get(link, headers=headers)
        r.raise_for_status()                    # If the response was successful, no Exception will be raised
        return False
    except Exception as err:
        eprint(f'Error occurred during URL Request: {err}')
        return True
    else:
        return False

#Print to std.err
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Function to process the stdin, return...
def process_stdin(stdin, option, crawl):
    buffer = ""
    if select.select([stdin,],[],[],0.0)[0]:
        eprint("The stdin is empty")
    for li in stdin:
        buffer = buffer + li
        #if option == "stdin_file":
            # if it finds an end of line
            #if li is None:
            #    documents.append(buffer)

    if option == "path":
        input_file = "lfiles.txt"
        with open(input_file, 'w') as filehandle:
            filehandle.write(buffer)
        process_lfiles(input_file=input_file, crawl=0, is_file=1)

    if option == "lsites":
        input_file = "lsites.txt"
        with open(input_file, 'w') as filehandle:
            filehandle.write(buffer)
        process_lwebsites(input_file=input_file, crawl=crawl)

    if option == "stdin_file":
        file = "index.html"
        print(buffer)
        with open(file, 'w') as filehandle:
            filehandle.write(buffer)
            domain_name = file
        geturls(url=file, domain_name=domain_name, crawl=0, is_file=1)



# Function that receives a list of websites and process them.
def process_lwebsites(input_file: str, crawl: bool) -> None:
    with open(input_file, "r") as f:
        info = f.readlines()
        for url in info:
            url = url.replace("\n", "").replace("\t", "").strip()
            print("Processing URL: ", url)
            domain_name = urlparse(url).netloc
            if "localhost" in url:
                crawl = 0
                geturls(url=url, domain_name=domain_name, crawl=crawl, is_file=0)
            else:
                geturls(url=url, domain_name=domain_name, crawl=crawl, is_file=0)

# Function that receives a list of files and process them
def process_lfiles(input_file: str, crawl: bool, is_file: bool) -> None:
    with open(input_file, "r") as f:
        info = f.readlines()
        for file_name in info:
            file_name = file_name.replace("\n", "").replace("\t", "").strip()
            print("Processing file: ", file_name)
            geturls(url=file_name, domain_name="", crawl=crawl, is_file=1)

# Function that prints a message and exit of the application
def printandexit(message) -> None:
    print(message)
    sys.exit(2)

def main(argv):
    ssl._create_default_https_context = ssl._create_unverified_context
    
    help_message = 'A Link Scrapper in Python \n\n Usage: python scrapper.py [option] [argument] \n\n -u, --url = url to crawl \n -c, --crawl [on/off]  = turn on or off crawl, default=on \n -f, --file [filepath] = a file path to parse, crawling deactivated in this option  \n -l --lfiles = list of files to parse (each line of the file must be a different file) \n -w --lwebsite = list of websites to check (each line of the file must be a different website), crawling deactivated in this option. If localhost, the crawling is deactivated in this option\n -S --stdin [option] for accept stdin input. Available options are: "f" to pipe the content of an html file,  "p" for a list of files, with "w" a list of websites, example: "cat listofwebsites.txt | python scrapper.py -S w"'
    badargument_message_url = "The only option to be use with -u, --url is --crawl, -c"
    badargument_message_lwebsite = "The only option  -l, --lwebsite is provide a list of websites, shouldnt be used with other parameter"
    badargument_message_stdin = "Stdin cannot be used with this options"
    try:
        opts, args = getopt.getopt(argv, "h:u:c:f:w:S:l:", ['help', 'url=', 'crawl=', 'file=', 'lfiles=', 'stdin=', 'lwebsite='])
    except getopt.GetoptError:
        printandexit(message=help_message)

    port: int = 3000
    crawl: bool = 0
    lwebsite: bool = 0
    lfiles: bool = 0
    urlselected: bool = 0
    fselect: bool = 0
    stdin: bool = 0
    given_url: str = "http://localhost"
    for opt, arg in opts:
        if opt == '-h':                         # help message
            printandexit(message=help_message)
        elif opt in ("-c", "--crawl"):         # activate/deactivate crawling
            if arg == "on":
                crawl = 1
            if arg == "off":
                crawl = 0
        elif opt in ("-f", "--file"):             # File path to parse
            fselect = 1
            crawl = 0                             # There is no crawling here, since there is no domain
            file_path = arg
            fname = ntpath.basename(arg)
            try:
                geturls(url=file_path, domain_name="", crawl=crawl, is_file=1)
            except IOError:
                print("Please choose a valid file path")
                sys.exit()
        elif opt in ("-u", "--url"):                 # url to crawl, decide whether it's a normal website or localhost
            urlselected = 1
            given_url = arg
            domain_name = urlparse(given_url).netloc
        elif opt in ("-S", "--Stdin"):
            stdin = 1
            option = "stdin_file"
            if arg == "f":
                option = "stdin_file"
            if arg == "w":
                option = "lsites"
            if arg == "p":
                option = "path"
        elif opt in ("-w", "--lwebsite"):
            input_file = arg
            lwebsite = 1
        elif opt in ("-l", "--lfiles"):
            input_file = arg
            lfiles = 1
        else:
            print("Parameter not recognized: %s !\n" % opt)
            print(help_message)
    #Options validations
    if (urlselected == 1 and fselect == 1) and (urlselected == 1 and lwebsite == 1) and (urlselected == 1 and stdin == 1):
        printandexit(message=badargument_message_url)
    if (lwebsite == 1 and stdin == 1) and (lwebsite == 1 and fselect == 1):
        printandexit(message=badargument_message_lwebsite)
    if (lfiles == 1 and stdin == 1) and (stdin == 1 and fselect == 1):
        printandexit(message=badargument_message_stdin)
    #Process the selected options
    if lwebsite == 1:
        process_lwebsites(input_file=input_file, crawl=crawl)
    if lfiles == 1:
        crawl = 0
        process_lfiles(input_file=input_file, crawl=crawl, is_file=1)
    if fselect == 1:
        crawl = 0
    if stdin == 1:
        process_stdin(stdin=sys.stdin, option=option, crawl=crawl)
    if urlselected == 1:
        if "localhost" not in given_url:
            geturls(url=given_url, domain_name=domain_name, crawl=crawl, is_file=0)
        else:   # For localhost, it needs to pass the port. Eg: time python3 scrapper.py -u http://localhost:3000
            crawl = 0
            geturls(url=given_url, domain_name=given_url, crawl=crawl, is_file=0)

if __name__ == "__main__":
    main(sys.argv[1:])

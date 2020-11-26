# IDENTIFYING DEAD LINKS ON A WEBSITE

The goal from this project is to the check for deadlinks on a website




# How to run
To identify deadlinks on a website run the command below

```
    ./nodeinstaller.sh -g [github repository] -p [port]
```

Obs:
* [github repository] = the link of the github repository. It must contain a node server inside it.
* [port] = the port used to run the server. The default port is 3000.
* The bash script installs all the requirments

# Scrapper

If you would like to run only the scrapper, you can run only the python script as described below.

```
      A Link Scrapper in Python 

 Usage: python scrapper.py [option] [argument] 

 -u, --url = url to crawl 
 -c, --crawl [on/off]  = turn on or off crawl, default=on 
 -f, --file [filepath] = a file path to parse, crawling deactivated in this option  
 -l --lfiles = list of files to parse (each line of the file must be a different file) 
 -w --lwebsite = list of websites to check (each line of the file must be a different website), 
                 crawling deactivated in this option. If localhost, the crawling is deactivated in this option
 -S --stdin [option] for accept stdin input. 
            Available options for --stdin are: "f" to pipe the content of an html file,  
            "p" for a list of files, with "w" a list of websites, example: "cat listofwebsites.txt | python scrapper.py -S w
 
```



## Libraries

 - requests
 - BeautifulSoup
 - typing


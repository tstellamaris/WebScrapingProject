from selenium import webdriver
import csv
import re

driver = webdriver.Chrome()

# Page that we want to scrape
driver.get("https://www.ted.com/talks/")

# Define the CSV file where the data will be stored
csv_file = open('tedtalks.csv', 'w', encoding='utf-8')
writer = csv.writer(csv_file)
# Write the header row
writer.writerow(['title', 'description', 'keywords', 'date', 'duration', 'views', 'n_lang', 'lang', 'speaker', 'speaker_job', 'speaker_about', 'n_comments'])

# Number of pages that we are going to scrape
number_pages = int(driver.find_elements_by_xpath('//div[@class="pagination"]/a')[-2].text)
print("Total of pages: {}".format(number_pages))
print('=' * 50)

# All urls of the main page that we are going to scrape
main_urls = ['https://www.ted.com/talks?page={}'.format(x) for x in range(1, number_pages + 1)]
all_detail_urls = []
index = 1

# Scraping each main page
for url in main_urls:
    # Check which page is been scraping
    print("Scraping page number " + str(index))
    
    driver.get(url)
    detail_urls = driver.find_elements_by_xpath('//h4[@class="h9 m5"]/a')
    print(str(len(detail_urls)) + " links is going to be scraped in this page")
    print('=' * 50)
    
    # Construct a list with the urls that is going to be scraped
    # We are going to get the data from these urls
    detail_urls = [x.get_attribute("href") for x in detail_urls]
    all_detail_urls.extend(detail_urls)
    index += 1

index = 1
print("Total of videos: {}".format(len(all_detail_urls)))
print('=' * 50)
# Scraping each video's page
for url in all_detail_urls:
    print("Scraping video number {} - {:0.2f}% completed".format(index, (index / len(all_detail_urls) * 100)))
    driver.get(url)
    result = {}
    
    # Data about the video
    result['title'] = driver.find_element_by_xpath('//meta[@itemprop="name"]').get_attribute('content')
    result['description'] = driver.find_element_by_xpath('//meta[@itemprop="description"]').get_attribute('content')
    result['keywords'] = driver.find_element_by_xpath('//meta[@name="keywords"]').get_attribute('content').replace("TED, talks, ", "")
    result['date'] = list(map(lambda x: x.text, driver.find_elements_by_xpath('//div[@class=" f:.9 p-x:3@md c:black t-a:l "]//span')))[-1].replace("| ","")
    result['duration'] = driver.find_element_by_xpath('//meta[@property="og:video:duration"]').get_attribute('content')
    result['views'] = driver.find_element_by_xpath('//meta[@itemprop="interactionCount"]').get_attribute('content')
    # Data about available subtitles languages
    language = list(filter(lambda x: x != '', map(lambda x: x.get_attribute('hreflang'), driver.find_elements_by_xpath('//link[@rel="alternate"]')[1:])))
    result['n_lang'] = len(language)
    result['lang'] = " | ".join(language)
    # Data about the speaker
    try:
        result['speaker'] = driver.find_element_by_xpath('//meta[@name="author"]').get_attribute('content')
    except:
        result['speaker'] = None    
    try:
        result['speaker_job'] = list(map(lambda x: x.text, driver.find_elements_by_xpath('//div[@class="m-b:.2"]//span')))[-1]
    except:
        result['speaker_job'] = None
    try:
        result['speaker_about'] = list(map(lambda x: x.text, driver.find_elements_by_xpath('//p[@class=" d:n d:b@md l-h:n m-b:.5 "]')))[0]
    except:
        result['speaker_about'] = None
    # Get the number os comments
    try:
        comments = list(filter(lambda x: x.find('Comments') != -1, map(lambda x: x.text, driver.find_elements_by_xpath('//ul[@class="c:black d:f o-x:s o-y:h p-t:.5 p-x:2 sl b-b:1 b-c:gray-l c:gray p-l:0@lg"]//span'))))[-1]
        result['n_comments'] = int(re.findall('\d+', comments)[0])
    except:
        result['n_comments'] = None


    index += 1
    writer.writerow(result.values())


csv_file.close()
driver.close()
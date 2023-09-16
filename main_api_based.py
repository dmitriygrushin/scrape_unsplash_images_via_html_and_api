""" instead of requests & beautifulsoup we'll use httpx & selectolax """
import os
from httpx import get
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

"""
    Scope Statement
        * write a python script that scrapes image from Unsplash
        * the utility should download the highest resolution image
            that pertains to a given keyword
        * premium/watermarked images should be excluded
        * for extra practice, explore HTML-based scraping & API-based route
            - for HTML-based scraping don't worry about pagination, so when you load the page it may only
                initially show ~20 images and to display more you need to click a button
                for this you would need to use a headless browser i.e. Selenium
            - for API-based scraping do consider pagination

        * sample interface
            scrape("water", 10)
"""


def get_response_for(keyword, results_per_page, page=1):
    """ The API is open. No need to set request headers like the browser this just works via the url """
    """
       Make GET req to API and return JSON res  
    """

    url = f"https://unsplash.com/napi/search/photos?query={keyword}&per_page={results_per_page}&page={page}"
    resp = get(url)

    # if response was successful then return the json
    return resp.json() if resp.status_code == 200 else None


def get_image_urls(data):
    """
        Unsplash gets images from the url that the json has

        get the json/dict from data and return the image url from:
            results: {0: Obj {id: ..., url: ..., premium: T/F, ...}, 1: Obj {...}, ...}
    """

    results = data["results"]

    # get the urls for the images from the json result above and make sure that the image is NOT premium
    img_urls = [x["urls"]["raw"] for x in results if x["premium"] is False]

    # remove the query strings from the urls to get the base url
    img_urls = [x.split("?")[0] for x in img_urls]

    # return the list of base urls
    return img_urls


def download_images(img_urls, max_download, dest_dir="images", tag=""):
    successfully_downloaded = 0

    for url in img_urls:
        if successfully_downloaded < max_download:
            # get/download the image from the url
            resp = get(url)

            # extract the file_name from the url
            file_name = url.split("/")[-1]  # gets you: "...", "...", ..., "photo-46504654-1f13g5"

            # create file path if path doesn't exist
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            with open(f"{dest_dir}/{tag}{file_name}.jpeg", "wb") as f:
                # save image
                f.write(resp.content)

                successfully_downloaded += 1
        else:
            break

    return successfully_downloaded


def scrape(keyword, num_of_results):
    # will be used for pagination in-case a page returns less than we need
    start_page = 1

    # amount of successful image downloads
    success_count = 0

    while success_count < num_of_results:
        # get JSON data
        data = get_response_for(keyword, results_per_page=20, page=start_page)

        # updated how many more image downloads are still needed. Initial would be: num_of_results - 0
        max_downloads = num_of_results - success_count

        if data:
            # pass the JSON data and get the base image urls as List
            img_urls = get_image_urls(data)

            # after downloading the images get the successful downloads and pass updated amount of downloads needed
            success_downloads = download_images(img_urls, max_downloads, tag=keyword)

            # update success count by adding successful downloads
            success_count += success_downloads

            # increment the pagination by 1 in-case you didn't get the amount of images needed from the current page
            start_page += 1
        else:
            print("Error: no data returns")
            break


if __name__ == '__main__':
    scrape("snowboarding", 3)
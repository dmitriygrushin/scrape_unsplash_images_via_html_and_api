""" instead of requests & beautifulsoup we'll use httpx & selectolax """
import os
from httpx import get
from selectolax.parser import HTMLParser
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

"""             ***************************************************
                *** USING THE API IS THE BEST WAY TO DO THIS    *** 
                *** THIS IS THE VERSION WITHOUT USING AN API    *** 
                *** HTML-BASED SCRAPING WAS USED TO DEMONSTRATE ***
                *************************************************** """

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


def get_img_tags_for(term=None):
    # more specific exception than python's if "None" was not used
    if not term:
        raise Exception("No search term provided")

    """
        get the HTML from unsplash url for the term
    """
    url = f"https://unsplash.com/s/photos/{term}"
    resp = get(url)

    """
        handle if get request was unsuccessful 
    """
    if resp.status_code != 200:
        raise Exception("Error getting response")

    """
        parse the HTML response and get the relevant HTML <img> tags 
    """
    tree = HTMLParser(resp.text)
    imgs = tree.css("figure a img[srcset][itemprop]")  # List of img tags using a Descendant Combinator
    return imgs


def img_filter_out(url: str, keywords: list) -> bool:
    """we want to filter out the url that contains the keywords"""

    # any(...) returns T if any item in an iterable are T, else F.
    # We use 'not' keyword to negate and say if it contains return false
    return not any(x in url for x in keywords)


def get_high_res_img_url(img_node):
    """
        srcset attribute has a str "www.abc.com/xyz 2000px, ..."
        so we take srcset and split the sizes into a list
    """
    srcset = img_node.attrs["srcset"]
    srcset_list = srcset.split(", ")

    """ srcset_list has a List of "link size" i.e. ["link size", "link size", ...]
        * get the link on it's own so we split the link and size by a space
        * filter out the keywords we don't want
        url_res now contains [[link, size], [link, size], ...]"""
    url_res = [src.split(" ") for src in srcset_list if img_filter_out(src, ['plus', 'profile', 'premium'])]

    """
        if url got filtered out then return none
    """
    if not url_res:
        return None

    """
        return the highest res version of the image
        1. split the link by '?' i.e. abc.com/xyz-photo-16543?...960px -> abc.com/xyz-photo-16543, ?...960px
        2. [abc.com/xyz-photo-16543, ?...960px] 
        3. return the base link which gives you the highest res image
    """
    return url_res[0][0].split("?")[0]


def save_images(img_urls, dest_dir="images", tag=""):
    # assuming happy path so no error checking
    for url in img_urls:
        resp = get(url)
        logging.info(f"Downloading {url}...")
        file_name = url.split("/")[-1]

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # wb: write binary - one way to save images
        with open(f"{dest_dir}/{tag}{file_name}.jpeg", "wb") as f:
            f.write(resp.content)
            logging.info(f"Saved {url}, wht size {round(len(resp.content) / 1024 / 1024, 2)} MB.")


""" when run:
    * directly: __name__ = __main__
    * imported: __name__ = main_html_based.py """


def main():
    search_tag = "tree"
    dest_dir = "tree"

    img_nodes = get_img_tags_for(search_tag)

    """
        List of all high resolution images with None
        for each image node get the high resolution version of it
        since there are multiple resolutions in the node's attributes
        all_img_urls now contains all the links for the high resolution versions of the images
    """
    all_img_urls = [get_high_res_img_url(i) for i in img_nodes]

    """
        List of all high resolution images without None
        make sure we don't get None in all_img_urls, why?
        notice how in get_high_res_img_url we return None "if not url_res: return None"
        meaning if the url got filtered out(i.e. premium image) then it will return None
    """
    img_urls = [u for u in all_img_urls if u]

    # Get first 3 images [:3] so you don't have to wait too long to test it
    # then just take the high resolution image url and download it
    save_images(img_urls[:3], dest_dir, search_tag)


if __name__ == '__main__':
    main()

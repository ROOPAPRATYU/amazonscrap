from selenium import webdriver
import time
import urllib.request
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import parse_qs, unquote
import pandas as pd
import re
base_url = "https://www.amazon.in/s"
search_query = "bags"
page_count = 20
driver = webdriver.Chrome()
columns = ["Product URL",'Href Link', "Product Name", "Product Price", "Product Rating", "Product Review", "Description", "Manufacturer","Product Description", "ASIN"]
dataframe = pd.DataFrame(columns=columns)
for page_number in range(1, page_count + 1):
    params = {
        "k": search_query,
        "page": page_number,
        "qid": 1653308124,
        "sprefix": "ba%2Caps%2C283",
        "ref": f"sr_pg_{page_number}"
    }
    
    # Construct the URL with query parameters
    url = base_url + "?" + "&".join(f"{key}={value}" for key, value in params.items())
    
    driver.get(url)
    page_source=driver.page_source
      # Add a delay to give the page time to load

    print(f"Page {page_number} title: {driver.title}")
    soup = BeautifulSoup(page_source, "html.parser")
    div=soup.find_all('div',{'class':'a-section a-spacing-small a-spacing-top-small'})
    for d in div:
        span_with_aria_label = d.find('span', {'aria-label': True})
        #print(d)
        if d.find('a',{'class':"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"}):
            a=d.find('a',{'class':"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
            print("======================\n")
           # print("PRODUCT URL => ",a.text.strip())
            product_url = a.get('href')  # Extract the href attribute to get the URL
            #print("======================\n")
            print("PRODUCT URL => ", product_url)
            print("PRODUCT NAME =>",a.text.strip())
            driver.execute_script("window.open(arguments[0], '_blank');", product_url)
            new_tab_handle = driver.window_handles[-1]  # Get the handle of the newly opened tab/window
            driver.switch_to.window(new_tab_handle)
            new_tab_url = driver.current_url
            print("New Tab URL:", new_tab_url)

            print("New Page Title:", driver.title)
            new_page_source = driver.page_source
            new_soup = BeautifulSoup(new_page_source, "html.parser")
            #print(new_soup)
            feature_bullets = new_soup.find('div', id='feature-bullets')
            if feature_bullets:
                print("DESCRIPTION =>\n")
                bullet_points = feature_bullets.find_all('span', class_='a-list-item')
                for bullet_point in bullet_points:
                    print(bullet_point.get_text(strip=True))
                    data_discription=bullet_point.get_text(strip=True)
            else:
                print("no tag found")
            div_element = new_soup.find('div', {'id': 'productDescription'})
            if div_element:
                span_element = div_element.find('span')
                if span_element:
                    text = span_element.get_text(strip=True)
                    print("PRODUCT DESCRIPTION=>", text)
                else:
                    text="No Description"
            else:
                text="No Description"
            rows = new_soup.find_all('tr')

            for row in rows:
                header = row.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
                if header and 'Manufacturer' in header.get_text():
                    manufacturer_data = row.find('td', class_='a-size-base prodDetAttrValue')
                    if manufacturer_data:
                        manufacturer = manufacturer_data.get_text(strip=True)
                        print("Manufacturer:", manufacturer)
                        break
            rows = new_soup.find_all('tr')
            for row in rows:
                header = row.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
                if header and 'ASIN' in header.get_text():
                    asin_data = row.find('td', class_='a-size-base prodDetAttrValue')
                    if asin_data:
                        asin = asin_data.get_text(strip=True)
                        print("ASIN:", asin)
                        break
            else:
                details_list = new_soup.find("div", id="detailBullets_feature_div")
                if details_list:
                    details_items = details_list.find_all("li")

                    for item in details_items:
                        item_text = item.get_text(strip=True)
                        if "Manufacturer" in item_text:
                            manufacturer = item_text.split(":")[1].strip()
                            print("Manufacturer:", manufacturer)
                        elif "ASIN" in item_text:
                            asin = item_text.split(":")[1].strip()
                            print("ASIN:", asin)
    
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        if d.find('div',{'class':"a-row a-size-base a-color-base"}):
            element=d.find('div',{'class':"a-row a-size-base a-color-base"})
            if element.find('span',{'class':"a-price"}):
                data=element.find('span',{'class':"a-price"})
                price_text = data.text.strip()
        
                price_parts = price_text.split('₹')
                if len(price_parts) > 1:
                    first_price = price_parts[1]
                    print("PRODUCT PRICE => ₹" + first_price)
                else:
                    print("Unable to extract price")
            else:
                print("no price found")
        if span_with_aria_label:
            aria_label = span_with_aria_label['aria-label']
            number = aria_label.replace(',', '')
            print("PRODUCT RATING =>:", number)
            next_span = span_with_aria_label.find_next_sibling('span', {'aria-label': True})
            if next_span:
                review_aria_label = next_span['aria-label']
                review_number = review_aria_label.replace(',', '')
                print("PRODUCT REVIEW =>:", review_number)
            else:
                print("no rating")
        
        else:
            continue
        scraped_data = {
            "Product URL": new_tab_url,
            'Href Link':product_url,
            "Product Name": a.text.strip(),
            "Product Price": first_price,
            "Product Rating": number,
            "Product Review": review_number,
            "Description": data_discription,  # Add your scraped description here
            "Manufacturer": manufacturer,  # Add your scraped manufacturer here
            "Product Description":text,
            "ASIN": asin  # Add your scraped ASIN here
        }
        dataframe = dataframe.append(scraped_data, ignore_index=True)
    
        time.sleep(2)
        
    time.sleep(2)
print(dataframe)
dataframe.to_csv("scraped_data_details.csv", index=False)
driver.quit()
#<div class="a-section a-spacing-small a-spacing-top-small"><div class="a-section a-spacing-none puis-padding-right-small s-title-instructions-style"><div class="a-row a-spacing-micro"><span class="a-declarative" data-version-id="v3b48cl1js792724v4d69zlbwph" data-render-id="r3nn77mvtnyskk2fdj6x36xny09" data-action="a-popover" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-a-popover" data-a-popover="{&quot;name&quot;:&quot;sp-info-popover-B0B69M182Q&quot;,&quot;position&quot;:&quot;triggerVertical&quot;,&quot;closeButton&quot;:&quot;true&quot;,&quot;dataStrategy&quot;:&quot;preload&quot;}" data-csa-c-id="f45maf-usvmsc-maxn9t-t1nadt"><a href="javascript:void(0)" role="button" style="text-decoration: none;" aria-label="View Sponsored information or leave ad feedback" class="puis-label-popover puis-sponsored-label-text"><span class="puis-label-popover-default"><span class="a-color-secondary">Sponsored</span></span><span class="puis-label-popover-hover"><span class="a-color-base">Sponsored</span></span> <span class="aok-inline-block puis-sponsored-label-info-icon"></span></a></span><div class="a-popover-preload" id="a-popover-sp-info-popover-B0B69M182Q"><div class="puis puis-v3b48cl1js792724v4d69zlbwph"><span>You are seeing this ad based on the product’s relevance to your search query.</span><div class="a-row"><span class="a-declarative" data-version-id="v3b48cl1js792724v4d69zlbwph" data-render-id="r3nn77mvtnyskk2fdj6x36xny09" data-action="s-safe-ajax-modal-trigger" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-s-safe-ajax-modal-trigger" data-s-safe-ajax-modal-trigger="{&quot;header&quot;:&quot;Leave feedback&quot;,&quot;dataStrategy&quot;:&quot;ajax&quot;,&quot;ajaxUrl&quot;:&quot;/af/sp-loom/feedback-form?pl=%7B%22adPlacementMetaData%22%3A%7B%22searchTerms%22%3A%22YmFncw%3D%3D%22%2C%22pageType%22%3A%22Search%22%2C%22feedbackType%22%3A%22sponsoredProductsLoom%22%2C%22slotName%22%3A%22TOP%22%7D%2C%22adCreativeMetaData%22%3A%7B%22adProgramId%22%3A1024%2C%22adCreativeDetails%22%3A%5B%7B%22asin%22%3A%22B0B69M182Q%22%2C%22title%22%3A%22uppercase+Medium+17+Ltrs+Vegan+Leather+%2814.6+inch%29+Laptop+Backpack+2300EBP1+3x+more+water+resistant+%22%2C%22priceInfo%22%3A%7B%22amount%22%3A1600.0%2C%22currencyCode%22%3A%22INR%22%7D%2C%22sku%22%3A%222300EBP1GRN%22%2C%22adId%22%3A%22A01510481XFFGFR81S748%22%2C%22campaignId%22%3A%22A03574293293QCS1NIO8S%22%2C%22advertiserIdNS%22%3Anull%2C%22selectionSignals%22%3Anull%7D%5D%7D%7D&quot;}" data-csa-c-id="ct27kk-yc4tj0-9lder2-nvlk2q"><a class="a-link-normal s-underline-text s-underline-link-text s-link-style" href="#"><span>Let us know</span> </a> </span></div></div></div></div><h2 class="a-size-mini a-spacing-none a-color-base s-line-clamp-2"><a class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTo4NTQyNDMyMjY0NTM4NjA4OjE2OTI2MzIzMjg6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692632328%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1"><span class="a-size-medium a-color-base a-text-normal">uppercase Medium 17 Ltrs Vegan Leather (upto 14 inch) Laptop Backpack 2300EBP1 3x more water resistant sustainable bags with rain proof zippers for Men, Women, Boys and Girls, 750 Days warranty</span> </a> </h2></div><div class="a-section a-spacing-none a-spacing-top-micro"><div class="a-row a-size-small"><span aria-label="4.0 out of 5 stars"><span class="a-size-base puis-normal-weight-text">4.0</span><span class="a-letter-space"></span><span class="a-declarative" data-version-id="v3b48cl1js792724v4d69zlbwph" data-render-id="r3nn77mvtnyskk2fdj6x36xny09" data-action="a-popover" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-a-popover" data-a-popover="{&quot;position&quot;:&quot;triggerBottom&quot;,&quot;popoverLabel&quot;:&quot;&quot;,&quot;url&quot;:&quot;/review/widgets/average-customer-review/popover/ref=acr_search__popover?ie=UTF8&amp;asin=B0B69M182Q&amp;ref=acr_search__popover&amp;contextId=search&quot;,&quot;closeButton&quot;:false,&quot;closeButtonLabel&quot;:&quot;&quot;}" data-csa-c-id="m41c3t-hytx72-yjln2x-ng34cz"><a href="javascript:void(0)" role="button" class="a-popover-trigger a-declarative"><i class="a-icon a-icon-star-small a-star-small-5 aok-align-bottom puis-review-star-single"><span class="a-icon-alt">4.0 out of 5 stars</span></i><i class="a-icon a-icon-popover"></i></a></span> </span><span aria-label="540"><a class="a-link-normal s-underline-text s-underline-link-text s-link-style" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTo4NTQyNDMyMjY0NTM4NjA4OjE2OTI2MzIzMjg6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692632328%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1#customerReviews"><span class="a-size-base s-underline-text"></span> </a> </span><span aria-label="(5-star: 54%)"><span class="a-size-base">(5-star: 54%)</span></span></div><div class="a-row a-size-base"><span class="a-size-base a-color-secondary">100+ bought in past month</span></div></div><div class="sg-row"><div class="sg-col sg-col-4-of-12 sg-col-4-of-16 sg-col-4-of-20 sg-col-4-of-24"><div class="sg-col-inner"><div class="a-section a-spacing-none a-spacing-top-micro puis-price-instructions-style"><div class="a-row a-size-base a-color-base"><a class="a-size-base a-link-normal s-no-hover s-underline-text s-underline-link-text s-link-style a-text-normal" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTo4NTQyNDMyMjY0NTM4NjA4OjE2OTI2MzIzMjg6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692632328%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1"><span class="a-price" data-a-size="xl" data-a-color="base"><span class="a-offscreen">₹1,600</span><span aria-hidden="true"><span class="a-price-symbol">₹</span><span class="a-price-whole">1,600</span></span></span> <div style="display: inline-block"><span class="a-size-base a-color-secondary">M.R.P: </span><span class="a-price a-text-price" data-a-size="b" data-a-strike="true" data-a-color="secondary"><span class="a-offscreen">₹2,100</span><span aria-hidden="true">₹2,100</span></span></div> </a> <span class="a-letter-space"></span><span>(24% off)</span><span class="a-letter-space"></span></div></div><div class="a-section a-spacing-none a-spacing-top-micro"><div class="a-row a-size-base a-color-secondary s-align-children-center"><div class="a-row s-align-children-center"><span class="aok-inline-block s-image-logo-view"><span class="aok-relative s-icon-text-medium s-prime"><i class="a-icon a-icon-prime a-icon-medium" role="img" aria-label="Amazon Prime"></i></span><span></span></span> </div><div class="a-row"><span aria-label="FREE delivery Fri, 25 Aug "><span class="a-color-base">FREE delivery </span><span class="a-color-base a-text-bold">Fri, 25 Aug </span></span></div></div></div><div class="a-section a-spacing-none a-spacing-top-mini s-color-swatch-container-list-view"><div class="a-section s-color-swatch-container s-quick-view-text-align-start"><div data-csa-c-type="link" data-csa-c-content-id="more-colors-message" data-csa-c-swatch-more-url="/sspa/click?ie=UTF8&amp;spc=MTo4NTQyNDMyMjY0NTM4NjA4OjE2OTI2MzIzMjg6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dacm_sr_dp_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692632328%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1" data-csa-c-swatch-remaining-count="+1 colour/pattern" data-csa-c-interaction-events="click" data-csa-c-id="x9yqbj-eabtup-7qps8w-8wnca8"><a class="a-link-normal s-color-swatch-link puis-spacing-small s-hidden-in-quick-view" href="/sspa/click?ie=UTF8&amp;spc=MTo4NTQyNDMyMjY0NTM4NjA4OjE2OTI2MzIzMjg6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dacm_sr_dp_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692632328%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1" role="link"><u>+1 colour/pattern</u></a></div></div></div></div></div><div class="sg-col sg-col-4-of-12 sg-col-4-of-16 sg-col-8-of-20 sg-col-8-of-24"><div class="sg-col-inner"></div></div></div></div>
#<a class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTozODQ1MDA4MjAxNDcwNjA0OjE2OTI2MzI2OTk6c3BfYnRmOjIwMTUzOTYyNDIxNDk4OjowOjo&amp;url=%2FFUR-JADEN-Anti-Theft-Backpack-Professionals%2Fdp%2FB0C28QQMFJ%2Fref%3Dsr_1_21_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692632699%26sprefix%3Dba%252Caps%252C283%26sr%3D8-21-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9idGY%26psc%3D1"><span class="a-size-medium a-color-base a-text-normal">FUR JADEN Pro Series Smart Tech Anti-Theft Laptop Backpack With USB-A and USB-C Type Charging Port for Men &amp; Women For Business Professionals &amp; College Students</span> </a>
#<div class="a-section a-spacing-none a-spacing-top-micro puis-price-instructions-style"><div class="a-row a-size-base a-color-base"><a class="a-size-base a-link-normal s-no-hover s-underline-text s-underline-link-text s-link-style a-text-normal" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTo3NDg5MjQ4MDc3NzI5MjE1OjE2OTI2NDAwMzI6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692640032%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1"><span class="a-price" data-a-size="xl" data-a-color="base"><span class="a-offscreen">₹1,600</span><span aria-hidden="true"><span class="a-price-symbol">₹</span><span class="a-price-whole">1,600</span></span></span> <div style="display: inline-block"><span class="a-size-base a-color-secondary">M.R.P: </span><span class="a-price a-text-price" data-a-size="b" data-a-strike="true" data-a-color="secondary"><span class="a-offscreen">₹2,100</span><span aria-hidden="true">₹2,100</span></span></div> </a> <span class="a-letter-space"></span><span>(24% off)</span><span class="a-letter-space"></span></div></div>
#<div class="a-row a-size-base a-color-base"><a class="a-size-base a-link-normal s-no-hover s-underline-text s-underline-link-text s-link-style a-text-normal" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTo3NDg5MjQ4MDc3NzI5MjE1OjE2OTI2NDAwMzI6c3BfYXRmOjIwMDYzNzg0NDU4Mzk4OjowOjo&amp;url=%2Fuppercase-Backpack-2300EBP1-repellent-sustainable%2Fdp%2FB0B69M182Q%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692640032%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1"><span class="a-price" data-a-size="xl" data-a-color="base"><span class="a-offscreen">₹1,600</span><span aria-hidden="true"><span class="a-price-symbol">₹</span><span class="a-price-whole">1,600</span></span></span> <div style="display: inline-block"><span class="a-size-base a-color-secondary">M.R.P: </span><span class="a-price a-text-price" data-a-size="b" data-a-strike="true" data-a-color="secondary"><span class="a-offscreen">₹2,100</span><span aria-hidden="true">₹2,100</span></span></div> </a> <span class="a-letter-space"></span><span>(24% off)</span><span class="a-letter-space"></span></div>
#<span class="a-price" data-a-size="xl" data-a-color="base"><span class="a-offscreen">₹1,600</span><span aria-hidden="true"><span class="a-price-symbol">₹</span><span class="a-price-whole">1,600</span></span></span>
#<span class="a-size-base puis-normal-weight-text">4.0</span>
#<span class="a-size-base s-underline-text">6</span>
#<a class="a-link-normal s-underline-text s-underline-link-text s-link-style" target="_blank" href="/sspa/click?ie=UTF8&amp;spc=MTo1MjExMTAxOTI5NzMwNjQ5OjE2OTI2NDQ2Njg6c3BfYXRmOjMwMDAxNjYxODE5NjUzMjo6MDo6&amp;url=%2FZebronics-Compartment-Backpacks-15-6-inch-Black%2Fdp%2FB0C6KZS555%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2M096C61O4MLT%26keywords%3Dbags%26qid%3D1692644668%26sprefix%3Dba%252Caps%252C283%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1#customerReviews"><span class="a-size-base s-underline-text">6</span> </a>
#<div id="feature-bullets" class="a-section a-spacing-medium a-spacing-top-small">                                                  <ul class="a-unordered-list a-vertical a-spacing-mini">  <li class="a-spacing-mini"><span class="a-list-item"> Care Instructions: Wipe with Damp Cloth  </span></li>  <li class="a-spacing-mini"><span class="a-list-item"> Number Lock: This Fur Jaden Anti Theft laptop backpack comes equipped with a Number Lock. This helps keep your laptop and other belongings safe when you need to leave your bag unattended in a public space. The number lock sequence can be changed and customised by your directly.&lt;br&gt;  </span></li>  <li class="a-spacing-mini"><span class="a-list-item"> USB Charging Port: Now charge your devices on the go with your new Fur Jaden backpack without the hassle of carrying a bulk power bank in your pocket/ hand at all times.&lt;br&gt;  </span></li>  <li class="a-spacing-mini"><span class="a-list-item"> Ergonomic Design: This backpack has been designed to ensure equal weight distribution on your shoulders along with padded shoulder straps and breathable air mesh on the back.&lt;br&gt;  </span></li>  <li class="a-spacing-mini"><span class="a-list-item"> Dimension: 42 CM (L) x 30 CM (W) x 18 CM (D). Storage Capacity: 25L. Weight: 600 Grams; Warranty: 1 Year Manufacturer Warranty against Manufacturing Defects&lt;br&gt;  </span></li>  <li class="a-spacing-mini"><span class="a-list-item"> Age Range Description: Adult; Closure Type: Zipper; Lining Description: Polyester&lt;br&gt;  </span></li>  </ul>   <!-- Loading EDP related metadata --></div>
#<div id="productDescription" class="a-section a-spacing-small">       <!-- show up to 2 reviews by default --><p> <span>Zebronics Camp1, 14 Liters, 1 Compartment Laptop Backpacks Fit Up to 15.6-inch Laptop, Polyester Fabric, Office Use and Mini Business Travel Bags</span>  </p>          </div>
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd

service = Service('.venv/chromedriver.exe')
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=service, options=options)

district = ["binh-tan", "binh-thanh", "go-vap", "phu-nhuan", "tan-binh", "tan-phu", "thu-duc"]

for d in  district:
    house_links = []
    for i in range(1, 101):
        try:
            url = f"https://muaban.net/bat-dong-san/ban-nha-quan-{d}-ho-chi-minh?page={i}"
            driver.get(url)
            time.sleep(3)

            house_elements = driver.find_elements(By.CSS_SELECTOR, "div.sc-q9qagu-2.FOmwc a.over")

            if not house_elements:
                print(f"Hết dữ liệu ở trang {i}, dừng quét!")
                break

            for house in house_elements:
                link = house.get_attribute("href")
                if link:
                    house_links.append(link)

        except NoSuchElementException:
            print("Không tìm thấy phần tử phù hợp!")
        except Exception as e:
            print("Lỗi:", str(e))

    print(f"Tìm thấy {len(house_links)} link nhà.")

    # Duyệt qua từng link để lấy thông tin chi tiết
    house_data = []
    for index, link in enumerate(house_links):
        try:
            driver.get(link)
            time.sleep(3)

            details = {}
            details["price"] = driver.find_element(By.CSS_SELECTOR, "div.price").text.strip()
            details["address"] = driver.find_element(By.CSS_SELECTOR, "div.address").text.strip()
            detail_elements = driver.find_elements(By.XPATH,
                                                   "/html/body/div/div[2]/div[2]/div[1]/div[2]/div[6]/div[1]/ul/li")
            if len(detail_elements) == 0:
                detail_elements = driver.find_elements(By.XPATH,
                                                       "/html/body/div/div[2]/div[2]/div[1]/div[2]/div[8]/div[1]/ul/li")

            for item in detail_elements:
                try:
                    label = item.find_element(By.CSS_SELECTOR, "span.label").text.strip()
                    value = item.find_element(By.CSS_SELECTOR, "span:not(.label)").text.strip()
                    details[label] = value
                except:
                    continue

            house_info = {
                "Giá": details.get("price", "N/A"),
                "Địa chỉ": details.get("address", "N/A"),
                "Loại hình nhà ở": details.get("Loại hình nhà ở:", "N/A"),
                "Diện tích đất": details.get("Diện tích đất:", "N/A"),
                "Số phòng ngủ": details.get("Số phòng ngủ:", "N/A"),
                "Số phòng vệ sinh": details.get("Số phòng vệ sinh:", "N/A"),
                "Tổng số tầng": details.get("Tổng số tầng:", "N/A"),
                "Hướng ban công": details.get("Hướng ban công:", "N/A"),
                "Hướng cửa chính": details.get("Hướng cửa chính:", "N/A"),
                "Giấy tờ pháp lý": details.get("Giấy tờ pháp lý:", "N/A")
            }
            house_data.append(house_info)
            print(f"{index + 1}. {house_info}")

        except Exception as e:
            print(f"Lỗi khi truy cập {link}: {str(e)}")


    # Chuyển dữ liệu thành DataFrame và lưu CSV
    df = pd.DataFrame(house_data)
    df.to_csv(f"Quan{d}.csv", index=False, encoding='utf-8-sig')
    print(df.head())

driver.quit()
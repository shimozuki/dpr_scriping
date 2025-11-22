from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import pandas as pd
from datetime import datetime

class InstagramScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self, username, password):
        try:
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            try:
                cookies_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]")
                cookies_btn.click()
                time.sleep(1)
            except:
                pass
            
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            password_input.send_keys(Keys.RETURN)
            time.sleep(15)
            
            try:
                not_now_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not now') or contains(text(), 'Not Now')]")
                not_now_btn.click()
                time.sleep(2)
            except:
                pass
            
            try:
                not_now_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
                not_now_btn.click()
                time.sleep(2)
            except:
                pass
            
            print("Login berhasil!")
            return True
            
        except Exception as e:
            print(f"Error saat login: {e}")
            return False
    
    def open_post(self, post_url):
        try:
            self.driver.get(post_url)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Error membuka post: {e}")
            return False
    
    def load_all_comments(self, max_scroll=120):
        try:
            try:
                view_all = self.driver.find_element(By.XPATH, "//button[contains(@class, '_acan') or contains(text(), 'View all')]")
                view_all.click()
                time.sleep(10)
            except:
                pass
            
            try:
                comments_section = self.driver.find_element(By.XPATH, 
                    "//div[contains(@class, 'x5yr21d') and contains(@class, 'xw2csxc') and contains(@class, 'x1odjw0f')]")
                
                print("Menemukan section scroll komentar...")
                scroll_count = 0
                last_height = self.driver.execute_script("return arguments[0].scrollHeight", comments_section)
                
                while scroll_count < max_scroll:
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_section)
                    time.sleep(2)
                    
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", comments_section)
                    
                    if new_height == last_height:
                        print("Sudah mencapai akhir komentar")
                        break
                        
                    last_height = new_height
                    scroll_count += 1
                    print(f"Scroll komentar {scroll_count}/{max_scroll}...")
                    
            except:
                print("Menggunakan scroll alternatif...")
                try:
                    comments_section = self.driver.find_element(By.XPATH, "//div[@role='dialog']//ul | //article//ul")
                    scroll_count = 0
                    last_height = self.driver.execute_script("return arguments[0].scrollHeight", comments_section)
                    
                    while scroll_count < max_scroll:
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_section)
                        time.sleep(2)
                        
                        new_height = self.driver.execute_script("return arguments[0].scrollHeight", comments_section)
                        
                        if new_height == last_height:
                            break
                            
                        last_height = new_height
                        scroll_count += 1
                        print(f"Scroll komentar {scroll_count}/{max_scroll}...")
                        
                except:
                    scroll_count = 0
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    while scroll_count < max_scroll:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        new_height = self.driver.execute_script("return document.body.scrollHeight")
                        
                        if new_height == last_height:
                            break
                            
                        last_height = new_height
                        scroll_count += 1
                        print(f"Scroll halaman {scroll_count}/{max_scroll}...")
            
            print("Selesai loading komentar")
            
        except Exception as e:
            print(f"Error saat load komentar: {e}")
    
    def scrape_comments(self):
        comments = []
        
        try:
            time.sleep(3)
            
            try:
                comment_list_items = self.driver.find_elements(By.XPATH, 
                    "//ul//li[contains(@class, 'x1lziwak')]")
                print(f"Metode 1: Menemukan {len(comment_list_items)} item komentar...")
                
                if len(comment_list_items) == 0:
                    comment_list_items = self.driver.find_elements(By.XPATH, "//ul/li")
                    print(f"Metode 2: Menemukan {len(comment_list_items)} item li...")
                
                if len(comment_list_items) == 0:
                    comment_list_items = self.driver.find_elements(By.XPATH, "//article//ul/li")
                    print(f"Metode 3: Menemukan {len(comment_list_items)} item komentar...")
                
                for item in comment_list_items:
                    try:
                        username_elem = item.find_element(By.XPATH, 
                            ".//span[contains(@class, '_ap3a')]")
                        username = username_elem.text.strip()
                        
                        comment_elem = item.find_element(By.XPATH, 
                            ".//span[contains(@class, 'x1lliihq') and contains(@class, 'x5n08af')]")
                        comment_text = comment_elem.text.strip()
                        
                        if username and comment_text and username != comment_text:
                            comments.append({
                                "username": username,
                                "comment": comment_text
                            })
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"Error metode li: {e}")
                
                username_elements = self.driver.find_elements(By.XPATH, 
                    "//span[contains(@class, '_ap3a') and contains(@class, '_aaco')]")
                
                comment_elements = self.driver.find_elements(By.XPATH, 
                    "//span[contains(@class, 'x1lliihq') and contains(@class, 'x5n08af')]")
                
                print(f"Metode fallback: {len(username_elements)} username, {len(comment_elements)} komentar...")
                
                for i in range(min(len(username_elements), len(comment_elements))):
                    try:
                        username = username_elements[i].text.strip()
                        comment_text = comment_elements[i].text.strip()
                        
                        if username and comment_text and username != comment_text:
                            comments.append({
                                "username": username,
                                "comment": comment_text
                            })
                    except:
                        continue
            
            seen = set()
            unique_comments = []
            for comment in comments:
                comment_tuple = (comment['username'], comment['comment'])
                if comment_tuple not in seen:
                    seen.add(comment_tuple)
                    unique_comments.append(comment)
            
            print(f"Total komentar ditemukan: {len(unique_comments)}")
            return unique_comments
            
        except Exception as e:
            print(f"Error saat scrape komentar: {e}")
            return []
    
    def save_to_json(self, comments, filename="comments.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comments, f, ensure_ascii=False, indent=4)
            print(f"Komentar berhasil disimpan ke {filename}")
        except Exception as e:
            print(f"Error menyimpan file: {e}")
    
    def save_to_excel(self, comments, filename="instagram_comments.xlsx"):
        try:
            if not comments:
                print("Tidak ada komentar untuk disimpan!")
                return
            
            df = pd.DataFrame(comments)
            df.insert(0, 'No', range(1, len(df) + 1))
            df['Waktu Scraping'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.columns = ['No', 'Username', 'Komentar', 'Waktu Scraping']
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Komentar Instagram')
                
                worksheet = writer.sheets['Komentar Instagram']
                
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    adjusted_width = min(max_length + 2, 60)
                    worksheet.column_dimensions[chr(65 + idx)].width = adjusted_width
                
                from openpyxl.styles import Font, Alignment
                for cell in worksheet[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            
            print(f"✓ Komentar berhasil disimpan ke {filename}")
            print(f"✓ Total komentar: {len(df)} baris")
            
        except Exception as e:
            print(f"Error menyimpan file Excel: {e}")
            print("Pastikan library pandas dan openpyxl sudah terinstall!")
            print("Install dengan: pip install pandas openpyxl")
    
    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    scraper = InstagramScraper()
    
    USERNAME = "r.obbiul.013"
    PASSWORD = "Robbi13@#$"
    POST_URL = "https://www.instagram.com/p/DOOm-zgE1zC/"
    
    try:
        if scraper.login(USERNAME, PASSWORD):
            if scraper.open_post(POST_URL):
                scraper.load_all_comments(max_scroll=20)
                comments = scraper.scrape_comments()
                
                print("\n=== Contoh Komentar ===")
                for i, comment in enumerate(comments[:5], 1):
                    print(f"{i}. @{comment['username']}: {comment['comment']}")
                
                scraper.save_to_excel(comments, "instagram_comments.xlsx")
        
    finally:
        time.sleep(3)
        scraper.close()
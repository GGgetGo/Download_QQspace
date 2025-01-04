import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 创建存储图片的文件夹
if not os.path.exists('images'):
    os.makedirs('images')

data = {}  # 用于存储说说数据
post_count = 0  # 计数器，用于记录获取的说说数量

try:
    # 创建Chrome浏览器实例
    driver = webdriver.Chrome()
    
    # 访问QQ空间
    driver.get("https://qzone.qq.com/")
    print("已进入QQ空间，请扫码登录")
    
    # 等待用户扫码登录，直到“好友动态”文本出现
    WebDriverWait(driver, 60).until(
        EC.text_to_be_present_in_element((By.XPATH, "//li[@type='friend']"), "好友动态")
    )
    
    print("登录成功，正在获取说说...")
    
    # 获取最近的说说列表
    for _ in range(2000):  # 滚动2000次，每次加载5条
        # 获取当前的说说列表
        new_posts = driver.find_elements(By.XPATH, "//li[contains(@class, 'f-single')]")
        
        # 打印最近的说说内容
        for post in new_posts[-5:]:  # 只打印新加载的5条
            user_nickname = ""
            time_info = ""
            content = ""
            image_urls = []
            
            try:
                # 提取用户昵称
                user_nickname = post.find_element(By.XPATH, ".//div[contains(@class, 'f-nick')]/a").text
            except Exception as e:
                print(f"提取用户昵称时发生错误: {str(e)}")
            
            try:
                # 提取时间
                time_info = post.find_element(By.XPATH, ".//span[contains(@class, 'state')]").text
            except Exception as e:
                print(f"提取时间时发生错误: {str(e)}")
            
            try:
                # 提取内容
                content = post.find_element(By.XPATH, ".//div[contains(@class, 'f-info')]").text
            except Exception as e:
                print(f"提取内容时发生错误: {str(e)}")
            
            try:
                # 提取图片链接
                image_elements = post.find_elements(By.XPATH, ".//img")
                for img in image_elements:
                    img_src = img.get_attribute("src")
                    if img_src:
                        image_urls.append(img_src)
                        # 下载图片
                        img_data = requests.get(img_src).content
                        img_name = os.path.join('images', img_src.split('/')[-1])
                        with open(img_name, 'wb') as handler:
                            handler.write(img_data)
            except Exception as e:
                print(f"提取图片时发生错误: {str(e)}")
            
            # 将数据存储到字典中
            if user_nickname:
                if user_nickname not in data:
                    data[user_nickname] = []
                data[user_nickname].append({
                    "time": time_info,
                    "content": content,
                    "images": image_urls
                })
                post_count += 1  # 增加计数器
            
            # 每10条说说保存一次数据
            if post_count % 10 == 0:
                with open('qzone_posts.json', 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                print(f"已保存{post_count}条说说数据到 qzone_posts.json")
        
        # 模拟滚动下滑
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待加载

    # 将剩余数据写入JSON文件
    with open('qzone_posts.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print("数据已保存到 qzone_posts.json")

    # 等待几秒查看结果
    time.sleep(5)
    
    # 关闭浏览器
    driver.quit()

except Exception as e:
    print(f"发生错误: {str(e)}")
    if 'driver' in locals():
        driver.quit()
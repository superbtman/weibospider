import os
import time
from io import BytesIO
import pymongo
from PIL import Image
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
import sys
sys.path.append(os.getcwd())
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME
# os.getcwd() 方法用于返回当前工作目录
TEMPLATES_FOLDER = os.getcwd() + '/sina/account_build/templates/'


class WeiboLogin():
    def __init__(self, username, password):
        os.system('pkill -f phantom')
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        # PhantomJS 诸如网络监测、网页截屏、无需浏览器的 Web 测试、页面访问自动化等。
        self.browser = webdriver.PhantomJS()
        self.browser.set_window_size(1050, 840)
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        # 登陆界面
        self.browser.get(self.url)
        # WebDriver提供两种类型的等待：显式等待和隐式等待
        # 显示等待使webdriver等待某个条件成立时继续执行，否则在达到最大时长抛出超时异常（TimeoutException）
        # EC.presence_of_element_located 判断元素是否存在
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))

        #  Element_to_be_clickable 判断元素是否能够点击
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))

        # 执行操作
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        try:
            # 获取验证码图片元素
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        except TimeoutException:
            print('未出现验证码')
            # 如果未出现验证码则跳转到下一个账号登陆
            self.open()
        time.sleep(2)
        # 获取验证码位置
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        # 在磁盘上读写文件的功能都是由操作系统提供的，现代操作系统不允许普通的程序直接操作磁盘，所以，读写文件就是请求操作系统打开一个文件对象（通常称为文件描述符），然后，通过操作系统提供的接口从这个文件对象中读取数据（读文件），或者把数据写入这个文件对象（写文件）。
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        # 由验证码的位置裁剪网页图片 左上右下
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 20
        # 像素点颜色相似度阈值
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                        pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def same_image(self, image, template):
        """
        识别相似验证码
        :param image: 待识别验证码
        :param template: 模板
        :return:
        """
        # 相似度阈值
        threshold = 0.99
        count = 0
        # 嵌套循环判断两个矩阵像素点 是否大致相同
        for x in range(image.width):
            for y in range(image.height):
                # 判断像素是否相同
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result > threshold:
            print('成功匹配')
            return True
        return False

    def detect_image(self, image):
        """
        匹配图片
        :param image: 图片
        :return: 拖动顺序
        """
        # listdir方法用于返回指定的文件夹包含的文件或文件夹的名字的列表
        for template_name in listdir(TEMPLATES_FOLDER):
            template = Image.open(TEMPLATES_FOLDER + template_name)
            # 判断这两张图片是否一样
            if self.same_image(image, template):
                # 返回顺序
                # 遍历文件名依次返回数字作为numbers
                numbers = [int(number) for number in list(template_name.split('.')[0])]
                print('拖动顺序', numbers)
                return numbers

    def move(self, numbers):
        """
        根据顺序拖动
        :param numbers:
        :return:
        """
        # 获得四个按点 遍历顺序为从左到右 从上到下 与验证码滑动顺序一样的遍历顺序
        circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ')
        # click(element=null)                         点击元素，参数为空时，鼠标在当前位置点击
        # send_keys(keys_to_send)                     向文本框发送文字、按键
        # move_to_element(element)                   鼠标悬浮在某元素上
        # perform()                                  执行所有存储在ActionChains中的动作
        dx = dy = 0
        for index in range(4):
            circle = circles[numbers[index] - 1]
            # 如果是第一次循环
            if index == 0:
                # 点击第一个按点
                # 移动到距某个元素（左上角坐标）多少距离的位置 move_to_element_with_offset()
                # 点击鼠标左键，不松开 click_and_hold()
                ActionChains(self.browser) \
                    .move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size['height'] / 2) \
                    .click_and_hold().perform()
            else:
                # 假装不是爬虫操作
                # 小幅移动次数
                times = 30
                # 拖动
                for i in range(times):
                    ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                    time.sleep(1 / times)
            # 如果是最后一次循环
            if index == 3:
                # 松开鼠标
                ActionChains(self.browser).release().perform()
            else:
                # 计算下一次偏移
                dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']

    def run(self):
        """
        破解入口
        :return:
        """
        self.open()
        # 获取验证码图片
        image = self.get_image('captcha.png')
        numbers = self.detect_image(image)

        # 根据顺序进行手势操作
        self.move(numbers)
        WebDriverWait(self.browser, 30).until(
            EC.title_is('我的首页')
        )
        cookies = self.browser.get_cookies()
        cookie = [item["name"] + "=" + item["value"] for item in cookies]
        cookie_str = '; '.join(item for item in cookie)
        self.browser.quit()
        return cookie_str


if __name__ == '__main__':
    # 在目录中新建一个account.txt文件，格式需要与account_sample.txt相同
    # 其实就是把www.xiaohao.shop买的账号复制到新建的account.txt文件中
    file_path = os.getcwd() + '/sina/account_build/account.txt'
    with open(file_path, 'rb') as f:
        lines = f.readlines()
    mongo_client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
    collection = mongo_client[DB_NAME]["account"]
    for line in lines:
        line = line.strip()
        username = line.split('----')[0]
        password = line.split('----')[1]
        print('=' * 10 + username + '=' * 10)
        try:
            cookie_str = WeiboLogin(username, password).run()
        except Exception as e:
            print(e)
            continue
        print('获取cookie成功')
        # 在数据库中插入或者更新数据
        try:
            collection.insert(
                {"_id": username, "password": password, "cookie": cookie_str, "status": "success"})
        except DuplicateKeyError as e:
            collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookie_str, "status": "success"}})

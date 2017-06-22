from selenium import webdriver

import json
import time

LINKEDIN_URL = 'https://www.linkedin.com'


class LinkedInBot(object):
    def __init__(self, src, lkdin_username, lkdin_password):
        self.src = src
        self.lkdin_username = lkdin_username
        self.lkdin_password = lkdin_password
        self.browser = webdriver.Firefox()

    def login(self):
        self.browser.get(LINKEDIN_URL)
        time.sleep(5)

        emf = self.browser.find_element_by_id('login-email')
        emf.clear()
        emf.send_keys(self.lkdin_username)

        time.sleep(2)

        pwf = self.browser.find_element_by_id('login-password')
        pwf.clear()
        pwf.send_keys(self.lkdin_password)

        time.sleep(2)

        self.browser.find_element_by_id('login-submit').click()

        time.sleep(10)

    def find_number_of_employees(self, lkdin_com_link):
        self.browser.get(lkdin_com_link)
        time.sleep(10)

        num = 0
        try:
            spane = self.browser.find_element_by_xpath(
                "//span[@class='org-company-employees-snackbar__see-all-employees-link']")

            txtf = spane.find_element_by_tag_name('strong')
            txt = txtf.get_attribute('innerHTML')
            if txt.startswith('See all'):
                stidx = len('See all ')
                eidx = len(txt) - len(' employees on Linkedin')

                numtxt = txt[stidx:eidx]
                num = int(numtxt.replace(',', '').replace('.', ''))
        except Exception as ex:
            print(ex)

        if num != 0:
            return num

        try:
            tb = self.browser.find_element_by_xpath("//td[@headers='org-insights-module__a11y-summary-total']")
            txt = tb.find_element_by_tag_name('span').get_attribute('innerHTML')
            txt = txt.replace(',', '').replace('.', '')
            num = int(txt)
        except Exception as ex:
            print(ex)

        return num

    def process_and_write(self, dst, snbread=0):
        fr = open(self.src, mode='r')

        for i in range(0, snbread):
            fr.readline()

        line = fr.readline()
        count = 0
        while line != '':
            try:
                tokens = line.strip('\n').split(',')
                num = self.find_number_of_employees(tokens[4])
                dst.write('%s, %s, %s, %s, %s \n' % (tokens[0], tokens[1], tokens[2], num, tokens[4]))
                dst.flush()
                count += 1
            except Exception as ex:
                print(ex)
            finally:
                line = fr.readline()

        return count

    def resume(self, snbread=0):
        print('Resume collecting number of employees, starting from row: ' + str(snbread))
        dst = open('./complete_output.csv', mode='a')
        nb = self.process_and_write(dst, snbread=snbread)
        print('Resume collecting number of employees, processed: ' + str(nb) + " rows")

        return nb

    def start(self):
        print('Resume collecting number of employees, starting from row: 0')
        dst = open('./complete_output.csv', mode='w')
        nb = self.process_and_write(dst, snbread=0)
        print('Resume collecting number of employees, processed: ' + str(nb) + " rows")

        return nb

    def stop(self):
        self.browser.delete_all_cookies()
        self.browser.quit()


if __name__ == '__main__':
    snbread = 0
    try:
        snbread = int(open('./.snbread.log').read())
    except Exception as ex:
        print(ex)

    nb = 0
    try:
        cred = json.load(open('./lkdin.json'))

        lkdbot = LinkedInBot('./output.csv', lkdin_username=cred.get('email'), lkdin_password=cred.get('password'))
        lkdbot.login()
        nb = lkdbot.resume(snbread) if 0 < snbread < 3000 else lkdbot.start()
        lkdbot.stop()
    except Exception as ex:
        print(ex)
    finally:
        fw = open('./.snbread.log', mode='w')
        fw.write(str(nb))

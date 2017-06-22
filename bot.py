import google as gs
from pyexcel_xlsx import get_data

import os
import os.path


class Bot(object):
    def __init__(self, xlsx_src, sheet_name='Sheet1', offset=1, search_page_size=5, search_stop=1):
        self.xlsx_src = xlsx_src
        self.sheet_name = sheet_name
        self.offset = offset
        self.search_page_size = search_page_size
        self.search_stop = search_stop

    def find_company_links(self, cn):
        com_link = ''
        for link in gs.search(cn, num=self.search_page_size, stop=self.search_stop):
            if link is not None:
                com_link = link
                break

        lkdin_link = ''
        for link in gs.search('linkedin ' + cn, num=self.search_page_size, stop=self.search_stop):
            if link is not None:
                lkdin_link = link
                break

        return com_link, lkdin_link

    def process_and_write(self, dst, fromidx=0):
        data = get_data(self.xlsx_src).get(self.sheet_name)
        count = 0
        try:
            for i in range(self.offset + fromidx, len(data)):
                ccode = data[i][0]
                cname = data[i][1]
                links = self.find_company_links(cname)
                dst.write('%s, %s, %s, %s, %s \n' % (ccode, cname, links[0], 'NA', links[1]))
                dst.flush()

                count += 1
        except Exception as ex:
            print(ex)

        return count

    def resume(self, nbread=0):
        print('Resume collecting company links, start from the row: ' + str(nbread + self.offset))
        dst = open('./output.csv', mode='a')
        nb = self.process_and_write(dst=dst, fromidx=nbread)
        print('Resume collecting company links and processed: ' + str(nb) + " rows")
        return nb

    def start(self):
        print('Start collecting company links, start from the row: ' + str(self.offset))
        dst = open('./output.csv', mode='w')
        nb = self.process_and_write(dst=dst, fromidx=0)
        print('Start collecting company links and processed: ' + str(nb) + " rows")


def start_bot():
    nbr = 0
    try:
        nbr = int(open('./.nbread.log').read())
    except Exception as ex:
        print(ex)

    nb = 0
    try:
        bot = Bot('3000_company_names.xlsx')
        nb = bot.resume(nbread=nbr) if 0 < nbr <= 3000 else bot.start()
    finally:
        fw = open('./.nbread.log', mode='w')
        fw.write(str(nbr + nb))
        fw.flush()
        print('Number of processed companies sofar: ' + str(nbr + nb))


'''
if __name__ == '__main__':
    nbr = 0
    try:
        nbr = int(open('./.nbread.log').read())
    except Exception as ex:
        print(ex)

    nb = 0
    try:
        bot = Bot('3000_company_names.xlsx')
        nb = bot.resume(nbread=nbr) if 0 < nbr <= 3000 else bot.start()
    except Exception as ex:
        print(ex)
    finally:
        fw = open('./.nbread.log', mode='w')
        fw.write(str(nbr + nb))
        fw.flush()
        print('Number of processed companies sofar: ' + str(nbr + nb))
'''

if __name__ == '__main__':
    for i in range(1, 20):
        try:
            try:
                os.remove(os.path.join(os.environ.get('HOME'), '.google-cookie'))
                print('Remove file .google-cookie')
            except Exception:
                pass
            start_bot()
        except Exception as ex:
            print(ex)

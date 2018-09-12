from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
from threading import Thread, Lock
from queue import Queue
from cv2 import imwrite,imdecode
from urllib.request import urlopen
from numpy import asarray
from tqdm import tqdm
import warnings

warnings.simplefilter("ignore")

class get_info:
    fn = None
    g = None
    link = None
    nmb = None
    lst = False
    def __init__(self):
        a = input("For search 1, for download with link 2 , for create a list 3, for open the file which belongs pins 4>>")
        a = a.strip()
        if(a == "1"):
            g = input("Search word >>")
            g = g.strip()
            get_info.nmb = int(input("How many image do yo want >>"))
            get_info.link = "https://tr.pinterest.com/search/pins/?q="+str(g)
            get_info.fn = g
        elif(a == "2"):
            g = input("Link >>")
            g = g.strip()
            get_info.nmb = int(input("How many image do yo want >>"))
            get_info.link = g
            spl = get_info.link.strip("/").split("/")
            get_info.fn = spl[-1] + "_" + spl[len(spl)-2]


        elif(a == "3"):
            list_jobs = []
            while True:
                g = input("For search 1, for add a link 2, for end list 3 >>")
                g = g.strip()
                if(g == "1"):
                    g = input("Search word >>")
                    g = g.strip()
                    nmb = int(input("How many image do yo want >>"))
                    link = "https://tr.pinterest.com/search/pins/?q=" + str(g)
                    fn = g
                    list_jobs.append({"nmb":nmb,"link":link,"fn":fn})

                elif(g == "2"):
                    g = input("Link >>")
                    g = g.strip()
                    nmb = int(input("How many image do yo want >>"))
                    link = g
                    spl = get_info.link.strip("/").split("/")
                    fn = spl[-1] + "_" + spl[len(spl) - 2]
                    list_jobs.append({"nmb": nmb, "link": link, "fn": fn})
                elif(g == "3"):
                    if(len(list_jobs) == 0):
                        print("You didn't add any job. Program will close in 3 seconds.")
                        time.sleep(3)
                        exit()
                    else:
                        get_info.lst = list_jobs

                    break

                else:
                    print("Wrong Number")
                    exit()

                print("-----------------------\n")

        elif(a == "4"):
            os.startfile(f"{os.getcwd()}/pins/")
            print("Done.")
            exit()

        else:
            print("Wrong Number")
            exit()

        try:
            os.system("cls")
        except:
            pass

class ilister:
    ilist = Queue()
    copy_l = []
    leni = 0
    def __init__(self):
        self.tqpr = tqdm(total=10+int(get_info.nmb), desc="Opening browser...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        self.tqpr.update()
        self.tqpr.set_description("Going to link...")
        driver.get(get_info.link)
        self.tqpr.update()
        self.tqpr.set_description("Link opened.")
        q = 0
        bfn = 0
        samen = 0
        self.tqpr.update()
        self.tqpr.set_description("Starting image mining...")
        self.tqpr.set_description("Founded -->")
        added = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if(int(len(driver.find_elements_by_tag_name('img'))) >= int(get_info.nmb)):
                break

            if(int(len(driver.find_elements_by_tag_name('img'))) <= 5):
                q += 1
                if(q == 10):
                    print(f"Error! I can't find enough image!(Limit is 5, and there is no 5 image in this page! ) ")
                    break

            if(bfn == int(len(driver.find_elements_by_tag_name('img'))) ):
                samen += 1
                if(samen == 10):
                    print(f"There is no enough image, breaking down... I'm gonna download {bfn} image")
                    get_info.nmb = bfn
                    break

            if added == 0:
                self.tqpr.update(int(len(driver.find_elements_by_tag_name('img'))) - added)

            added = self.tqpr.last_print_n - 10
            if added > 0 or self.tqpr.last_print_n == 2:
                try:
                    self.tqpr.update(int(len(driver.find_elements_by_tag_name('img'))) - added)
                except:
                    pass

            bfn = int(len(driver.find_elements_by_tag_name('img')))

            time.sleep(0.5)

        images = driver.find_elements_by_tag_name('img')
        self.tqpr.update()
        self.tqpr.set_description("Starting to edit images...")

        try:
            os.mkdir("pins/"+get_info.fn)
        except:
            pass
        q = 0
        for image in images:
            if(q >= int(get_info.nmb)):
                break
            item = (image.get_attribute('src').replace("236x","564x"),q)
            ilister.copy_l.append(item)
            ilister.ilist.put(item)
            q += 1
        ilister.leni = ilister.ilist.qsize()
        self.tqpr.update()
        self.tqpr.set_description("Edit done...")
        self.tqpr.set_description("Starting download...")
        driver.close()
        self.tqpr.close()

class downloader:
    time1 = None
    q = 0
    def __init__(self):
        downloader.time1 = time.time()
        downloader.q = 0
        self.tqdbar = tqdm(total = get_info.nmb, desc=f"Downloading to 'pins/{get_info.fn}' ")
        for i in range(5):
            t = Thread(target = self.checker)
            t.daemon = True
            t.start()

        ilister.ilist.join()
        del ilister.ilist
        ilister.ilist = Queue()

    def downloader2(self,image):
        number = image[1]
        image = image[0]

        imwrite(f"pins/{get_info.fn}/{get_info.fn}{number}.jpg",imdecode(asarray(bytearray(urlopen(image).read()), dtype="uint8"), -1))
        downloader.q += 1

    def checker(self):
        while True:
            image = ilister.ilist.get()
            a_t = time.time()
            self.downloader2(image)
            self.tqdbar.update()
            ilister.ilist.task_done()

class check_done:
    def __init__(self):
        lst = ilister.copy_l
        self.lst = lst

    def check_done(self):
        if(len(os.listdir(f"pins/{get_info.fn}")) == len(self.lst)):
            print(1)
            return True
        elif(len(os.listdir(f"pins/{get_info.fn}")) > len(self.lst)):
            print(2)
            return False

        elif(len(os.listdir(f"pins/{get_info.fn}")) < len(self.lst)):
            didntdown = self.find_didnt_downloaded()
            print("I can't downloaded those images:")
            print(didntdown)

        else:
            print(3)
            return False

    def find_didnt_downloaded(self):
        numbers = []
        all_numbers = [n for n in range(get_info.nmb)]
        for image in os.listdir(f"pins/{get_info.fn}"):
            image = image.replace(get_info.fn,"")
            print(image)
            image = image.split(".")
            numbers.append(image[-2])
        print(numbers)
        numbers.sort()

        c = [each if not all_numbers.count(each) else None for each in numbers]
        d = list(filter(lambda a: a != None, c))
        return d

get_info()
lock = Lock()

if(get_info.lst != False):
    for job in get_info.lst:
        get_info.nmb = job["nmb"]
        get_info.link = job["link"]
        get_info.fn = job["fn"]
        ilister()
        if(ilister.leni <= 5):
            print(f"I can't find any image about {get_info.fn}")
        elif(ilister.leni > 5):
            downloader()
            print(f"{get_info.fn} downloaded in {int(time.time() - downloader.time1)} seconds.")

else:
    ilister()
    if (ilister.leni <= 5):
        print(f"I can't find any image about {get_info.fn}")
    elif (ilister.leni > 5):
        downloader()
        check_done().check_done()




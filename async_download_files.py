import os
import sys
import aiofiles 
from PIL import Image
import asyncio
from contextlib import closing
import shutil
import aiohttp
import tqdm
import time
urls = []
OUTPUT_FOLDER = "librarybooks"
FILES_PATH = os.path.join(OUTPUT_FOLDER, "files")
cookies = {
    'PHPSESSID': 'h9i7ji958j3vufec7nejlv7dqd',
    'user_auth': 'MjAwMTYwMDA4ODYyMTBAMjMzOV8yMzM5X2RhYTc3MDJjYzk5YzMzMDBiOWQ2MjE2Y2Y3NzRiN2VjZWM0Njc2OGFfMTY4NTM1MzM1MF8xNjg1Mzk2MjUx',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    # 'Cookie': 'PHPSESSID=h9i7ji958j3vufec7nejlv7dqd; user_auth=MjAwMTYwMDA4ODYyMTBAMjMzOV8yMzM5X2RhYTc3MDJjYzk5YzMzMDBiOWQ2MjE2Y2Y3NzRiN2VjZWM0Njc2OGFfMTY4NTM1MzM1MF8xNjg1Mzk2MjUx',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
}

running=True
async def main(loop):
    progress_queue = asyncio.Queue()
    for pos in range(5):
        progress_queue.put_nowait(pos)

    async with aiohttp.ClientSession(loop=loop, cookies=cookies) as session:
        tasks = [download(session, url, progress_queue) for url in urls]
        return await asyncio.gather(*tasks)

async def download(session, url, progress_queue):
    try:
        os.makedirs(FILES_PATH, exist_ok=True)
        async with session.get(url) as response:
            target = os.path.join(FILES_PATH, str(urls.index(url)).zfill(3)+ f"_{NAME}.jpeg")
            size = int(response.headers.get('content-length', 0)) or None
            position = await progress_queue.get()

            progressbar = tqdm.tqdm(
                desc=str(urls.index(url)).zfill(3)+ f"_{NAME}.jpeg", total=size, position=position, leave=False, unit='B', unit_scale=True, unit_divisor=1024
            )

            with open(target, mode='wb') as f, progressbar:
                async for chunk in response.content.iter_chunked(512):
                    f.write(chunk)
                    progressbar.update(len(chunk))

            await progress_queue.put(position)
            return target
    except:
        print("Whoops! Something Went wrong... Are you sure you set all values?")
def pdf_conv():
    try:
        image_1 = Image.open(os.path.join(FILES_PATH, f'000_{NAME}.jpeg'))
        im_1 = image_1.convert('RGB')
        image_list =[im_1]
        for image in os.listdir(FILES_PATH):
            if os.path.getsize(os.path.join(FILES_PATH, image)) < 10 * 1024:
                os.remove(os.path.join(FILES_PATH, image))
        for image in os.listdir(FILES_PATH):
            if f'{NAME}.jpeg' in image:
                image_list.append(Image.open(os.path.join(FILES_PATH, image)).convert('RGB'))   
        image_list.pop(0)
        im_1.save(os.path.join(OUTPUT_FOLDER, f'{NAME}.pdf'), save_all=True, append_images=image_list)
        shutil.rmtree(FILES_PATH)
    except NameError:
        print("Invalid File Name")
        menu()
def menu():
    global pages
    global NAME
    global FILES_PATH
    opt = input("""
    +----+-----------------------+
    |  1 | Set Book ID           |
    |  2 | Set Output Directory  |
    |  3 | Download Images       |
    |  4 | Convert Images to PDF |
    |  5 | Set File Name         |
    |  6 | Set No. of Pages      |
    |  7 | Quit                  |
    +----+-----------------------+
    """)
    match opt:
        case '1':
            try:
                BOOK_ID = input('Enter Book ID: ')
                for i in range(1, int(pages)):
                    urls.append(f'https://galwaypubliclibrariesie.librarypass.com/reader/image/{BOOK_ID}/{str(i)}/0')
                print(chr(27) + "[2J")
            except:
                print(chr(27) + "[2J")
                print("Whoops! Something Went wrong... Are you sure you set all values?")
        case '2':
            try:
                OUTPUT_FOLDER = input('Enter Directory Path: ')
                print(chr(27) + "[2J")
            except:
                print(chr(27) + "[2J")
                print("Whoops! Something Went wrong... Are you sure you set all values?")
        case '3':
            try:
                st = time.time()
                with closing(asyncio.get_event_loop()) as loop:
                    for tgt in loop.run_until_complete(main(loop)):
                        pass
                et = time.time()
                elapsed_time = et - st
                print(chr(27) + "[2J")
                print(f'Downloaded {pages} files in {elapsed_time} seconds')
            except:
                print(chr(27) + "[2J")
                print("Whoops! Something Went wrong... Are you sure you set all values?")
        case '4':
            try:
                pdf_conv()
                print(chr(27) + "[2J")
                print('Done!')
            except:
                print(chr(27) + "[2J")
                print("Whoops! Something Went wrong... Are you sure you set all values?")
        case '5': 
            try:
                NAME = input("Enter File Name: ")
                FILES_PATH = os.path.join(FILES_PATH, NAME)
                print(chr(27) + "[2J")
            except:
                print(chr(27) + "[2J")
                print("Whoops! Something Went wrong... Are you sure you set all values?")
        case '6':
            try:
                pages = input("Enter number of pages: ")
                print(chr(27) + "[2J")
            except:
                print(chr(27) + "[2J")
                print("Whoops! Something Went wrong... Are you sure you set all values?")
        case '7':
            running=False
            sys.exit(0)
        case '8': 
            print(urls)
try:
    print(""""
 █████   ██      ██    ██  ██   ██  █ ███████     
██   ██  ██       ██  ██    ██ ██     ██          
███████  ██        ████      ███      ███████     
██   ██  ██         ██      ██ ██          ██     
██   ██  ███████    ██     ██   ██    ███████     
                                             
                                             
██       ██████   ██████   ██                   
██       ██   ██  ██   ██  ██                   
██       ██████   ██   ██  ██                   
██       ██       ██   ██  ██                   
███████  ██       ██████   ███████              
                                             
                                             

""")
    time.sleep(1)
    while running:
        menu()
except ValueError or NameError:
    print(chr(27) + "[2J")
    print("Whoops! Something Went wrong... Are you sure you set all values?")

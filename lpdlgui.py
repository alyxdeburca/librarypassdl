import asyncio
import os
import shutil
import sys
import time
from contextlib import closing
import shutil
import aiohttp
import tqdm
from PIL import Image
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDialog,
                             QFileDialog, QInputDialog, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton, QSpinBox,
                             QVBoxLayout, QWidget, QDialogButtonBox)
urls=[]
cookies = {
    'PHPSESSID': 'h9i7ji958j3vufec7nejlv7dqd',
    'user_auth': 'MjAwMTYwMDA4ODYyMTBAMjMzOV8yMzM5X2RhYTc3MDJjYzk5YzMzMDBiOWQ2MjE2Y2Y3NzRiN2VjZWM0Njc2OGFfMTY4NTM1MzM1MF8xNjg1Mzk2MjUx',
}
LIBRARY_ID = 'galwaypubliclibrariesie'
async def main(loop):
    progress_queue = asyncio.Queue()
    for pos in range(5):
        progress_queue.put_nowait(pos)

    async with aiohttp.ClientSession(loop=loop, cookies=cookies) as session:
        tasks = [download(session, url, progress_queue) for url in urls]
        return await asyncio.gather(*tasks)

async def download(session, url, progress_queue):
    try:
        async with session.get(url) as response:
            target = os.path.join(FILES_PATH, str(urls.index(url)).zfill(3) + f"_{NAME}.jpeg")
            size = int(response.headers.get('content-length', 0)) or None
            position = await progress_queue.get()

            progressbar = tqdm.tqdm(
                desc=str(urls.index(url)).zfill(3) + f"_{NAME}.jpeg", total=size, position=position, leave=False,
                unit='B', unit_scale=True, unit_divisor=1024
            )

            with open(target, mode='wb') as f, progressbar:
                async for chunk in response.content.iter_chunked(512):
                    f.write(chunk)
                    progressbar.update(len(chunk))

            await progress_queue.put(position)
            return target
    except Exception as e:
        print("Fuck?", url, e)

def pdf_conv(OUTPUT_FOLDER):
    try:
        image_1 = Image.open(os.path.join(FILES_PATH, f'000_{NAME}.jpeg'))
        im_1 = image_1.convert('RGB')
        image_list = [im_1]

        for image in os.listdir(FILES_PATH):
            if os.path.getsize(os.path.join(FILES_PATH, image)) < 10 * 1024:
                os.remove(os.path.join(FILES_PATH, image))

        for image in os.listdir(FILES_PATH):
            if f'{NAME}.jpeg' in image:
                image_list.append(Image.open(os.path.join(FILES_PATH, image)).convert('RGB'))

        image_list.pop(0)
        im_1.save(os.path.join(OUTPUT_FOLDER, f'{NAME}.pdf'), save_all=True, append_images=image_list)
        shutil.rmtree(FILES_PATH)
    except NameError as e:
        print("Invalid File Name", e)
class InputForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Set Inputs")

        # Create form elements
        self.book_id_label = QLabel("Book ID:")
        self.book_id_input = QLineEdit()

        self.output_dir_input = QPushButton("Output Directory:")
        self.output_dir_input.clicked.connect(self.set_output_directory)

        self.download_images_checkbox = QCheckBox("Download Images")
        self.convert_to_pdf_checkbox = QCheckBox("Convert to PDF")

        self.NAME_label = QLabel("File Name:")
        self.NAME_input = QLineEdit()

        self.pages_label = QLabel("Number of Pages:")
        self.pages_input = QSpinBox()
        self.pages_input.setMinimum(1)
        self.pages_input.setMaximum(1000)

        self.library_id_label = QLabel("Library ID:")
        self.library_id_input = QLineEdit()

        self.mangasee_mode_checkbox = QCheckBox("Mangasee Mode")

        self.chapter_label = QLabel("Chapter:")
        self.chapter_input = QLineEdit()

        self.confirm_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.book_id_label)
        layout.addWidget(self.book_id_input)
        layout.addWidget(self.output_dir_input)
        layout.addWidget(self.download_images_checkbox)
        layout.addWidget(self.convert_to_pdf_checkbox)
        layout.addWidget(self.NAME_label)
        layout.addWidget(self.NAME_input)
        layout.addWidget(self.pages_label)
        layout.addWidget(self.pages_input)
        layout.addWidget(self.library_id_label)
        layout.addWidget(self.library_id_input)
        layout.addWidget(self.mangasee_mode_checkbox)
        layout.addWidget(self.chapter_label)
        layout.addWidget(self.chapter_input)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)

        self.confirm_button.accepted.connect(self.accept)
        self.confirm_button.rejected.connect(self.reject)

    def set_output_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Set Output Directory")
        if folder:
            self.OUTPUT_FOLDER = folder
            self.FILES_PATH = os.path.join(self.OUTPUT_FOLDER, "files")
            os.makedirs(self.FILES_PATH, exist_ok=True)
        return folder
    def reject(self):
        exit(app.exec_)
class MainWindow(QMainWindow):  
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        global FILES_PATH
        global mode
        global pages
        global CHAPTER
        global NAME
        global urls  
        form = InputForm(self)

        if form.exec_() == QDialog.Accepted:
            book_id = form.book_id_input.text()
            output_dir = form.OUTPUT_FOLDER
            download_images = form.download_images_checkbox.isChecked()
            convert_to_pdf = form.convert_to_pdf_checkbox.isChecked()
            NAME = form.NAME_input.text()
            pages = form.pages_input.value()
            library_id = form.library_id_input.text()
            mangasee_mode = form.mangasee_mode_checkbox.isChecked()
            chapter = form.chapter_input.text()

            # Do something with the input values
            print("Book ID:", book_id)
            print("Output Directory:", output_dir)
            print("Download Images:", download_images)
            print("Convert to PDF:", convert_to_pdf)
            print("File Name:", NAME)
            print("Number of Pages:", pages)
            print("Library ID:", library_id)
            print("Mangasee Mode:", mangasee_mode)
            print("Chapter:", chapter)
            FILES_PATH = os.path.join(form.OUTPUT_FOLDER, 'files')
            
            if download_images:
                if mangasee_mode:
                    for i in range(1, int(pages)):
                        urls.append(f'https://official.lowee.us/manga/{book_id}/{chapter.zfill(4)}-{str(i).zfill(3)}.png')
                else:
                    for i in range(1, int(pages)):
                        urls.append(f'https://{library_id}.librarypass.com/reader/image/{book_id}/{str(i)}/0')
                try:
                    st = time.time()
                    with closing(asyncio.get_event_loop()) as loop:
                        for tgt in loop.run_until_complete(main(loop)):
                            print('fuck')
                            pass
                    et = time.time()
                    elapsed_time = et - st
                    print(f'Downloaded {pages} files in {elapsed_time} seconds')
                except Exception as e:
                    print(chr(27) + "[2J")
                    print("Whoops! Something Went wrong... Are you sure you set all values?", e)
            if convert_to_pdf:
                pdf_conv(form.OUTPUT_FOLDER)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
    sys.exit()

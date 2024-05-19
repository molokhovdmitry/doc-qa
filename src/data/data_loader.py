import os
import zipfile
import chardet
from difflib import get_close_matches
from tqdm import tqdm


class DataLoader():
    def __init__(
            self,
            zip_path: str = 'data/data.zip',
            extract_dir: str = 'data/extracted'
            ) -> None:
        self.zip_file = zipfile.ZipFile(zip_path)
        self.files = []
        self.html_to_file = {}
        self.extract_dir = extract_dir
        self.txt_name_to_url = {}
        self.html_to_txt_name = {}
        self.html_to_url = {}

        # Extract and fill `html_to_file`
        for i, f in enumerate(self.zip_file.filelist):
            # Get extension and create new filename
            ext = '.' + f.filename.split('.')[-1]
            filename = 'file_{0:03}'.format(i) + ext

            # Save actual filename
            self.html_to_file[f.filename] = filename

            # Change filename and extract
            f.filename = filename
            self.zip_file.extract(f, path=self.extract_dir)

        # Fill `txt_name_to_url`
        for file in self.html_to_file.values():
            if file.split('.')[-1] == 'txt':
                file_path = os.path.join(self.extract_dir, file)
                self.txt_name_to_url.update(self.txt_to_dict(file_path))

        # Fill `html_to_txt_name`
        htmls = []
        for file in self.html_to_file.keys():
            if file.split('.')[-1] == 'html':
                htmls.append(file)

        print("Comparing html names to names from txt files...")
        for html in tqdm(htmls):
            # Get name without extension and department name
            name = html.split('/')[-1][:-5]
            # Find closest matches from txt
            matches = get_close_matches(
                name,
                self.txt_name_to_url,
                n=1,
                cutoff=0.35
            )
            # Raise an error if no matches for html
            try:
                assert len(matches) > 0
            except AssertionError as e:
                print(f"Did not find a match for {name}.\
                       Try lowering the cutoff value.")
                raise e
            # Add best match to `html_to_txt_name`
            self.html_to_txt_name[html] = matches[0]

        # Fill `html_to_url`
        for html, txt_name in self.html_to_txt_name.items():
            url = self.txt_name_to_url[txt_name]
            self.html_to_url[html] = url

        # Fill `files`
        for html, url in self.html_to_url.items():
            data = {
                'path': os.path.join(
                    self.extract_dir, self.html_to_file[html]),
                'name': html.split('/')[-1][:-5],
                'full_html_name': html,
                'department': html.split('/')[0],
                'url': url
            }
            self.files.append(data)

    def txt_to_dict(self, txt_path: str) -> dict:
        result = {}
        separator = ';http://'

        # Try detecting txt encoding. If did not detect the encoding,
        # try using `cp1251`
        detected_encoding = self.get_txt_encoding(txt_path)
        if not detected_encoding:
            encoding = 'cp1251'
        else:
            encoding = None

        # Get key-value pairs
        with open(txt_path, 'r', encoding=encoding) as file:
            for i, line in enumerate(file):
                line = line.strip()
                if line:
                    if separator in line:
                        key, value = line.split(';http://')
                        result[key] = separator[1:] + value
        return result

    def get_txt_encoding(self, txt_path: str) -> str:
        with open(txt_path, 'rb') as file:
            detector = chardet.universaldetector.UniversalDetector()
            for line in file:
                detector.feed(line)
            if detector.done:
                detector.close()
                return detector.result['encoding']
        return None

    def __getitem__(self, index: int) -> dict:
        return self.files[index]

import os
import zipfile
import pickle
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

        """
        Extract files from zip archive with new filenames and
        map new filenames to old filenames.
        """
        for i, f in enumerate(self.zip_file.filelist):
            # Get extension and create new filename
            ext = '.' + f.filename.split('.')[-1]
            filename = 'file_{0:03}'.format(i) + ext

            # Save actual filename
            self.html_to_file[f.filename] = filename

            # Change filename and extract
            f.filename = filename
            self.zip_file.extract(f, path=self.extract_dir)

        """
        Read txt files that map html file names to urls and create a mapping.
        These html file names are not the same as actual filenames.
        """
        for file in self.html_to_file.values():
            if file.split('.')[-1] == 'txt':
                file_path = os.path.join(self.extract_dir, file)
                self.txt_name_to_url.update(self.txt_to_dict(file_path))

        # Load only html files from `html_to_file`
        htmls = []
        for file in self.html_to_file.keys():
            if file.split('.')[-1] == 'html':
                htmls.append(file)

        """
        Compare html names to html names from txt files with difflib
        and create `html_to_txt_name` mapping. If the mapping already exists
        then load from file.
        """
        html_to_url_path = os.path.join(self.extract_dir, 'html_to_url.pkl')
        if os.path.exists(html_to_url_path):
            with open(html_to_url_path, 'rb') as f:
                self.html_to_url = pickle.load(f)
        else:
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

            # Create mapping from actual html name to url from txt files
            for html, txt_name in self.html_to_txt_name.items():
                url = self.txt_name_to_url[txt_name]
                self.html_to_url[html] = url

            # Save `html_to_url` mapping
            with open(html_to_url_path, 'wb') as f:
                pickle.dump(self.html_to_url, f)

        # Fill `files` that will contain all required metadata for every html
        for html, url in self.html_to_url.items():
            data = {
                'source': os.path.join(
                    self.extract_dir, self.html_to_file[html]),
                'name': html.split('/')[-1][:-5],
                'full_html_name': html,
                'department': html.split('/')[0],
                'url': url
            }
            self.files.append(data)

    def txt_to_dict(self, txt_path: str) -> dict:
        """
        The function `txt_to_dict` reads a text file, extracts key-value pairs
        separated by a specific
        separator, and returns them as a dictionary.
        :param txt_path: The `txt_path` parameter in the `txt_to_dict`
        function is a string that
        represents the file path to the text file from which you want to read
        data and convert it into a
        dictionary
        :type txt_path: str
        :return: The `txt_to_dict` method returns a dictionary containing
        key-value pairs extracted from
        a text file specified by the `txt_path` parameter. The keys are
        extracted from lines in the text
        file before the separator `';http://'`, and the values are extracted
        after the separator. The
        method handles text encoding detection and uses `cp1251` encoding
        as a fallback if the encoding
        is not detected.
        """
        result = {}
        separator = ';http://'

        """
        Try detecting txt encoding. If did not detect the encoding,
        try using `cp1251`
        """
        detected_encoding = self.get_txt_encoding(txt_path)
        if not detected_encoding:
            encoding = 'cp1251'
        else:
            encoding = detected_encoding
        # Get key-value pairs
        with open(txt_path, 'r', encoding=encoding, errors='ignore') as file:
            for i, line in enumerate(file):
                line = line.strip()
                if line:
                    if separator in line:
                        key, value = line.split(';http://')
                        result[key] = separator[1:] + value
        return result

    def get_txt_encoding(self, txt_path: str) -> str:
        """
        The function `get_txt_encoding` reads a text file and detects its
        encoding using the `chardet`
        library.
        :param txt_path: The `txt_path` parameter in the `get_txt_encoding`
        function is a string that
        represents the file path to the text file for which you want
        to detect the encoding. This
        function reads the text file in binary mode and uses the `chardet`
        library to detect the
        encoding of the text
        :type txt_path: str
        :return: The function `get_txt_encoding` reads a text file at the
        specified path in binary mode,
        detects the encoding of the text in the file using the `chardet`
        library, and returns the
        detected encoding as a string.
        """
        with open(txt_path, 'rb') as file:
            detector = chardet.universaldetector.UniversalDetector()
            for line in file:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
        return detector.result['encoding']

    def __getitem__(self, index: int) -> dict:
        return self.files[index]

    def __len__(self) -> int:
        return len(self.files)

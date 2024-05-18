import os
import zipfile
import chardet


class DataLoader():
    def __init__(
            self,
            zip_path: str = 'data/data.zip',
            extract_dir: str = 'data/extracted'
            ) -> None:
        self.zip_file = zipfile.ZipFile(zip_path)
        self.files = []
        self.name_to_file = {}
        self.extract_dir = extract_dir
        self.txt_name_to_link = {}

        # Extract and fill `name_to_file`
        for i, f in enumerate(self.zip_file.filelist):
            # Get extension and create new filename
            ext = '.' + f.filename.split('.')[-1]
            filename = 'file_{0:03}'.format(i) + ext

            # Save actual filename
            self.name_to_file[f.filename] = filename

            # Change filename and extract
            f.filename = filename
            self.zip_file.extract(f, path=self.extract_dir)

        # Fill `txt_name_to_link`
        for file in self.name_to_file.values():
            if file.split('.')[-1] == 'txt':
                file_path = os.path.join(self.extract_dir, file)
                self.txt_name_to_link.update(self.txt_to_dict(file_path))

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
                    print(txt_path, i, encoding)
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

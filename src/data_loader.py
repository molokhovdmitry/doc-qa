import os
import zipfile
import pickle
from bs4 import BeautifulSoup
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
        self.html_to_url = {}

        """
        Extract files from zip archive with new filenames and
        map new filenames to old filenames.
        """
        for i, f in enumerate(self.zip_file.filelist):
            # Get extension and create new filename
            ext = '.' + f.filename.split('.')[-1]
            if ext == '.html':
                filename = 'file_{0:03}'.format(i) + ext

                # Save actual filename
                self.html_to_file[f.filename] = filename

                # Change filename and extract
                f.filename = filename
                self.zip_file.extract(f, path=self.extract_dir)

        """
        Find confluence urls in html files and create mappings
        or load the mappings if they exist.
        """
        html_to_url_path = os.path.join(self.extract_dir, 'html_to_url.pkl')
        if os.path.exists(html_to_url_path):
            # Load the mappings
            with open(html_to_url_path, 'rb') as f:
                self.html_to_url = pickle.load(f)
        else:
            print("Searching for confluence URLs...")
            for html in tqdm(self.html_to_file):
                html_path = os.path.join(
                    self.extract_dir,
                    self.html_to_file[html]
                )
                url = self.get_confluence_url(html_path)
                self.html_to_url[html] = url

            # Save the mappings
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

    def get_confluence_url(self, path: str) -> str:
        """Returns a confluence url from html file."""
        with open(path, 'r') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        link_element = soup.find('link', rel='canonical')
        url = link_element['href']
        return url

    def __getitem__(self, index: int) -> dict:
        return self.files[index]

    def __len__(self) -> int:
        return len(self.files)

`DataLoader` class takes path to `.zip` file as an input, extracts the files with changed file names, matches `.html` file names to names in `.txt` files and creates an iterable object.

Assuming we are starting the app from the project root directory with:
```
python -m src.bot.main
```
We can use the class like this:
```
data = DataLoader(
    zip_path='data/data.zip',
    extract_dir='data/extracted'
)
```
And then iterate through the files in a loop:
```
for file in data:
    print(file)
```
Where `file` is a `Dict`:
```
{
    'source': 'path to file',
    'name': 'actual file name without extension',
    'full_html_name': 'full file name',
    'department': 'department name',
    'url': 'url'
}
```

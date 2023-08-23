import yaml
import requests
from tqdm import tqdm

from utils import load_configs


def download(url: str, file_name: str):

    print(f'### download start - {file_name}')

    response = requests.get(url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    print(total_size_in_bytes)

    with open(file_name, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
  
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    
    print(f'### download end - {file_name}')


if __name__ == '__main__':
    config = load_configs('./configs/default.yaml')

    for key in ['acoustic', 'rhythmizer', 'vocoder']:
        url = config[key]['url']
        file_name = config[key]['filename']
        download(url, file_name)
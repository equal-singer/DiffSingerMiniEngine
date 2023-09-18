import argparse
import glob
import json
import logging
import os.path
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import soundfile

import synthesis
import utils


SERVER_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_ROOT = os.path.join(SERVER_ROOT, 'configs')
ACOUSTIC_ROOT = os.path.join(SERVER_ROOT, 'assets', 'acoustic')

config = {}
dictionary = {}
dict_pad = -1
phoneme_list = []
vowels = set()
vocoder_path = ''
cache = './'
pool: ThreadPoolExecutor
tasks = {}
piles = {}
failures = {}


def init_config():
    parser = argparse.ArgumentParser(description='Start DiffSinger inference server')
    parser.add_argument('--config', type=str, required=False, default='default')
    args = parser.parse_args()
    
    cfg_path = os.path.join(CONFIG_ROOT, f'{args.config}.yaml')
    config.update(utils.load_configs(cfg_path))

    dict_path = config['dictionary']['filename']
    if not os.path.isabs(dict_path):
        dict_path = os.path.join(SERVER_ROOT, dict_path)
    dict_pad = config['dictionary']['reserved_tokens']
    dictionary.update(utils.load_dictionary(dict_path))
    vowels.update(utils.dictionary_to_vowels(dictionary))

    phoneme_list.extend(utils.dictionary_to_phonemes(dictionary, dict_pad))
    vocoder_path = config['vocoder']['filename']
    if not os.path.isabs(vocoder_path):
        vocoder_path = os.path.join(SERVER_ROOT, vocoder_path)
    assert os.path.exists(vocoder_path), 'Vocoder model not found. Please check your configuration.'

    cache = config['server']['cache_dir']
    if not os.path.isabs(cache):
        cache = os.path.join(SERVER_ROOT, cache)

    pool = ThreadPoolExecutor(max_workers=config['server']['max_threads'])


def models():
    res = {
        'models': [os.path.basename(file)[:-5] for file in glob.glob(os.path.join(ACOUSTIC_ROOT, '*.onnx'))]
    }
    
    print(res)


def rhythm():
    example = '''
        {
          "notes": [
            {
              "key": 0,
              "duration": 0.5,
              "slur": false,
              "phonemes": [
                "SP"
              ]
            },
            {
              "key": 69,
              "duration": 0.5,
              "slur": false,
              "phonemes": [
                "sh",
                "a"
              ]
            },
            {
              "key": 71,
              "duration": 1.0,
              "slur": true
            }
          ]
        }
    '''

    request = json.loads(example)
    ph_seq, ph_dur = synthesis.predict_rhythm(request['notes'], phoneme_list, vowels, config)

    res = {
        'phonemes': [
            {
                'name': name,
                'duration': duration
            }
            for name, duration in zip(ph_seq, ph_dur)
        ]
    }

    print(res)


def submit():
    example = '''
        {
          "model": "acoustic",
          "phonemes": [
            {
              "name": "SP",
              "duration": 0.5
            },
            {
              "name": "SP",
              "duration": 0.5
            }
          ],
          "f0": {
            "timestep": 0.01,
            "values": [
              440.0,
              440.0,
              440.0,
              440.0,
              440.0
            ]
          },
          "speedup": 50
        }
    '''

    request = json.loads(example)
    if 'speedup' not in request:
        request['speedup'] = config['acoustic']['speedup']
    token = utils.request_to_token(request)
    cache_file = os.path.join(cache, f'{token}.wav')

    _execute(request, cache_file, token)


def _execute(request: dict, cache_file: str, token: str):
    logging.info(f'Task \'{token}\' begins')
    
    try:
        wav = synthesis.run_synthesis(
            request, phoneme_list,
            os.path.join(ACOUSTIC_ROOT, f'{request["model"]}.onnx'),
            config
        )
        os.makedirs(cache, exist_ok=True)
        soundfile.write(cache_file, wav, config['vocoder']['sample_rate'])
        logging.info(f'Task \'{token}\' finished')
    except Exception as e:
        failures[token] = str(e)
        logging.error(f'Task \'{token}\' failed')
        logging.error(str(e))
        raise e


if __name__ == '__main__':
    init_config()

    # models()
    # rhythm()
    submit()
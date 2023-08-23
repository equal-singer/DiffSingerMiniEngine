Docker Run
```
Docker run -it -p 9266:9266 -v /코드있는 경로:/code --name diff-singer-mini python:3.8 bash
```

디펜던시 설치
```
pip install -r requirements.txt
```

모델 다운로드
```
python init.py
```

서버 실행 (port: 9266)
```
python server.py
```

--------------------------------------

# DiffSingerMiniEngine
A minimum inference engine for DiffSinger MIDI-less mode.

## Getting Started

1. Install `onnxruntime` following the [official guidance](https://onnxruntime.ai/).
2. Install other dependencies with `pip install PyYAML soundfile`.
3. Download ONNX version of the NSF-HiFiGAN vocoder from [here](https://github.com/openvpi/vocoders/releases/tag/nsf-hifigan-v1) and unzip it into `assets/vocoder` directory.
4. Download an ONNX rhythm predictor from [here](https://github.com/openvpi/DiffSinger/releases/tag/v1.4.1) and put it into `assets/rhythmizer` directory.
5. Put your ONNX acoustic models into `assets/acoustic` directory.
6. Edit `configs/default.yaml` or create another config file according to your preference and local environment.
7. Run server with `python server.py` or `python server.py --config <YOUR_CONFIG>`.

## API Specification

TBD

## How to Obtain Acoustic Models

1. [Train with your own dataset](https://github.com/openvpi/DiffSinger/blob/refactor/pipelines/no_midi_preparation.ipynb) or download pretrained checkpoints from [here](https://github.com/openvpi/DiffSinger/releases/tag/v1.4.0).
2. Export PyTorch checkpoints to ONNX format. See instructions [here](https://github.com/openvpi/DiffSinger/blob/refactor/docs/README-SVS-onnx.md).

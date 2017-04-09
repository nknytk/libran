# 環境構築手順

Raspberry Piの設定と、動作に必要な依存ライブラリをインストールする手順。

* [必要環境](#必要環境)
* [初期設定](#初期設定)
* [OpenCV](#opencv)
* [Julius](#julius)
* [OpenJtalk](#openjtalk)
* [Libran](#Libran)

## 必要環境

### 必要なハードウェアと周辺環境

以下の環境を前提とする。

* Raspberry Pi 3 Type B
    - Raspberry Pi Type B(初代)でも動作するが、音声入力に対する反応が遅いため推奨しない
    - ストレージとして16GB以上のmicroSDカード
* マイク付きUSB Webカメラが接続されていること
* Raspberry PiのAudio mini端子スピーカーが接続されていること
* インターネットに接続できること

### ハードウェアの配置

現時点では、自身が出力した音声を入力から除外する機能を備えていない。  
そのため、スピーカーから出力される音声がマイクに拾われないよう、スピーカー・マイクの配置と感度を調整する必要がある。  
また、ユーザーの上半身全体が画角に収まるよう、ユーザーからある程度離れた位置にカメラを置く必要がある。

設置例:

```
   |webcam with mic|




|speaker|    |speaker|

         user
```



## 初期設定

まず諸々最新化する。

```
sudo apt-get update && sudo apt-get upgrade
```

次に、ロケールを日本に変更する。また、GUIを使用しない場合はGPUへの割当メモリを減らす。  
`sudo raspi-config`でraspi-configを起動し、以下のように設定

* 4 Location Options
    - I1 Change Local > ja_JP.UTF-8 UTF-8 を選択
    - I2 Change Timezone > Asia > Tokyo
    - I4 Change Wi-fi Country > JP Japan
* 7 Advanced Options
    - A3 Memory Split > 16

(チェックボックスをon/offするにはSpaceキーを使用する)

## OpenCV

GitHubからOpenCV 3.1.0をダウンロードし、コンパイルしてインストールする。

```
sudo apt install libopencv-dev cmake git libgtk2.0-dev python3-dev python3-numpy libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev libqt4-dev  libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 libopenexr-dev python3-tk libeigen3-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev libqt4-dev libqt4-opengl-dev sphinx-common texlive-latex-extra default-jdk ant libvtk5-qt4-dev libdc1394-22-dev libdc1394-22 libdc1394-utils

wget -O 3.1.0.zip "https://github.com/opencv/opencv/archive/3.1.0.zip"
unzip 3.1.0.zip
cd opencv-3.1.0/
mkdir build
cd build/
sudo cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D INSTALL_PYTHON_EXAMPLES=ON -D PYTHON_EXECUTABLE=$(which python3) -D BUILD_opencv_python3=ON -D BUILD_opencv_python2=ON BUILD_EXAMPLES=ON -D WITH_FFMPEG=OFF -D  BUILD_opencv_java=OFF BUILD_opencv_test_java=OFF ..
sudo make -j 4
sudo make install
```

Python3を通じてOpenCVでWebカメラを利用できることを確認する。

```
python3
>>> import cv2
>>> v = cv2.VideoCapture(0)
>>> _ok, pic = v.read()
>>> v.release()
>>> pic is not None
```

## Julius

依存ライブラリをインストールし、snd-pcm-ossモジュールを有効化して再起動する。

```
sudo apt-get install alsa-utils sox libsox-fmt-all
sudo sh -c "echo snd-pcm-oss >> /etc/modules"
sudo reboot
```

Julius本体をダウンロードし、コンパイル

```
wget -O v4.4.2.zip "https://github.com/julius-speech/julius/archive/v4.4.2.zip"
unzip v4.4.2.zip
cd julius-4.4.2
./configure
make
```

ディクテーションキットをダウンロード

```
wget -O dictation-kit-v4.4.zip "https://osdn.net/frs/redir.php?m=iij&f=%2Fjulius%2F66544%2Fdictation-kit-v4.4.zip"
unzip dictation-kit-v4.4.zip
```

Juliusを起動し、`<<<　please speak　>>>`と表示されたら話してみる。  

```
AUDIODEV=/dev/dsp1 ALSADEV="plughw:1,0" ./julius-4.4.2/julius/julius -C ./julius-4.4.2/dictation-kit-v4.4/main.jconf -C ./julius-4.4.2/dictation-kit-v4.4/am-gmm.jconf -nostrip
```

認識結果が標準出力に表示されたら成功。

## OpenJtalk

open-jtalkと音声ファイルをインストールする。

```
sudo apt-get install open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001
wget http://downloads.sourceforge.net/project/mmdagent/MMDAgent_Example/MMDAgent_Example-1.7/MMDAgent_Example-1.7.zip
unzip MMDAgent_Example-1.7.zip
sudo cp -r MMDAgent_Example-1.7/Voice/mei /usr/share/hts-voice/
```

音量を100%に設定して、スピーカーから音声を出力できることを確認する。

```
amixer cset numid=1 100%
echo "こんにちは" > hello.txt
open_jtalk -m /usr/share/hts-voice/mei/mei_normal.htsvoice -x /var/lib/mecab/dic/open-jtalk/naist-jdic -ow hello.wav hello.txt
aplay hello.wav
```

## Libran

githubからソースコードを取得する。

```
git clone https://github.com/nknytk/libran
```

Python3のvirtualenvを作り、必要なパッケージをインストールする。

```
sudo apt-get install python3-pip mecab mecab-ipadic mecab-ipadic-utf8 libmecab-dev
sudo pip3 install virtualenv
virtualenv --system-site-packages .venv
. .venv/bin/activate
pip install chainer==1.20.0 Pillow bs4 mecab-python3 romkan
```

`config.json`の、`notification`要素のうち、`class`以外の要素を使用するメールアカウントに合わせて書き換える。

Libranを起動する。

```
python libran.py
```

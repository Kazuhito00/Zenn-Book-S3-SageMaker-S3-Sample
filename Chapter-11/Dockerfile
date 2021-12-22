FROM nvidia/cuda:11.4.2-cudnn8-runtime-ubuntu20.04

# ワークディレクトリ変更
ENV PROGRAM_DIR=/opt/program
WORKDIR $PROGRAM_DIR

# aptパッケージ インストール
RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
         wget \
         python3-pip \
         python3-setuptools \
         ca-certificates \
         cmake \
         libgl1-mesa-dev \
         libglib2.0-0 \
         libsm6 \
         libxrender1 \
         libxext6 \
    && rm -rf /var/lib/apt/lists/*

# python実行パス シンボリックリンク指定
RUN ln -s /usr/bin/python3 /usr/bin/python

# pipパッケージ インストール
COPY requirements.txt $PROGRAM_DIR/requirements.txt
RUN pip3 install --upgrade pip
RUN pip --no-cache-dir install -r requirements.txt

# 標準出力・標準エラーのストリームのバッファリングを行わない
ENV PYTHONUNBUFFERED=TRUE
# .pyc を生成しない
ENV PYTHONDONTWRITEBYTECODE=TRUE
# パス指定
ENV PATH="/opt/program:${PATH}"

# scriptsディレクトリコピー、実行権限付与
COPY scripts /opt/program
RUN chmod +x /opt/program/train

RUN mkdir /opt/program/model
COPY model /opt/program/model

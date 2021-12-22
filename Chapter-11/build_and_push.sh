#!/usr/bin/env bash

# イメージ名・タグ名指定
image=$1

if [ "$image" == "" ]
then
    echo "Usage: $0 <image-name>"
    exit 1
fi

# IAM認証情報に紐付くアカウント番号を取得
echo Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]
then
    exit 255
fi

# 現在のリージョン情報を取得(指定がない場合「us-west-2」に設定)
echo Get the region defined ~~
region=$(aws configure get region)
region=${region:-us-west-2}

# ECRへプッシュする名称を生成
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

# リポジトリがECRに存在しない場合、新規作成
echo If the repository doesnt exist in ECR, create it
aws ecr describe-repositories --repository-names "${image}" > /dev/null 2>&1
if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${image}" > /dev/null
fi

# ECRからログインコマンドを取得し、Dockerログインを実行
echo Get the login command from ECR and execute it directly
aws ecr get-login-password --region "${region}" | docker login --username AWS --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com

# Dockerビルド・プッシュ
echo docker build  -t ${image} .
docker build  -t ${image} .
echo docker tag ${image} ${fullname}
docker tag ${image} ${fullname}

docker push ${fullname}

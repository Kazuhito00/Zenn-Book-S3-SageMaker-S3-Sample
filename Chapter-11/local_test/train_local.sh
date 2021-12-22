#!/bin/sh
mkdir -p test_dir/model
mkdir -p test_dir/output

rm -f test_dir/model/*
rm -f test_dir/output/*

image=$1
docker run -v $(pwd)/test_dir:/opt/ml --rm ${image} train

#!/usr/bin/env python
import copy

import cv2
import numpy as np
import onnxruntime

class RoadSegmentation(object):

    def __init__(
        self,
        model_path,
        input_shape=[512, 896],
        score_th=0.5,
        providers=['CPUExecutionProvider'],
    ):
        # モデル読み込み
        self.onnx_session = onnxruntime.InferenceSession(model_path, providers=providers)

        self.input_name = self.onnx_session.get_inputs()[0].name
        self.output_name = self.onnx_session.get_outputs()[0].name

        # 各種設定
        self.input_shape = input_shape
        self.score_th = score_th

    def inference(self, image):
        image_width, image_height = image.shape[1], image.shape[0]

        # 前処理
        input_image = cv2.resize(image, dsize=(self.input_shape[1], self.input_shape[0]))
        input_image = np.expand_dims(input_image, axis=0)
        input_image = input_image.astype('float32')

        # 推論
        result = self.onnx_session.run([self.output_name], {self.input_name: input_image})

        # 後処理
        segmentation_map = result[0]
        segmentation_map = np.squeeze(segmentation_map)
        segmentation_map = cv2.resize(
            segmentation_map,
            dsize=(image_width, image_height),
            interpolation=cv2.INTER_LINEAR,
        )

        return segmentation_map

    def draw(self, image, mask):
        image_width, image_height = image.shape[1], image.shape[0]

        # サイズ調整
        debug_image = copy.deepcopy(image)
        segmentation_map = cv2.resize(
            mask,
            dsize=(image_width, image_height),
            interpolation=cv2.INTER_LINEAR,
        )

        color_image_list = []
        # ID 0:BackGround
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = (0, 0, 0)
        color_image_list.append(bg_image)
        # ID 1:Road
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = (255, 0, 0)
        color_image_list.append(bg_image)
        # ID 2:Curb
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = (0, 255, 0)
        color_image_list.append(bg_image)
        # ID 3:Mark
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = (0, 0, 255)
        color_image_list.append(bg_image)

        # セグメンテーションマップ頂上表示
        masks = segmentation_map.transpose(2, 0, 1)
        for index, mask in enumerate(masks):
            # スコア確認
            mask = np.where(mask > self.score_th, 0, 1)

            # 描画
            mask = np.stack((mask, ) * 3, axis=-1).astype('uint8')
            mask_image = np.where(mask, debug_image, color_image_list[index])
            debug_image = cv2.addWeighted(debug_image, 0.5, mask_image, 0.5, 1.0)

        return debug_image

if __name__ == '__main__':
    # モデル読み込み、ONNXセッション準備
    road_seg_model = RoadSegmentation('model/road_segmentation.onnx')

    # 動画読み込み
    video_capture = cv2.VideoCapture('sample.mp4')

    while True:
        # フレーム取得
        ret, frame = video_capture.read()
        if not ret:
            break

        # 推論
        road_seg_map = road_seg_model.inference(frame)
        debug_image = road_seg_model.draw(frame, road_seg_map)

        # 表示        
        cv2.imshow('Road Sementation', debug_image)
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Fruit slashing ninja game

The new main file (main_vision.py) uses opencv and mediapipe to control the "player"

To run the one using hand movements the following mediapipe model is needed\
[storage.googleapis.com...](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task)

To play the game the following directories are needed:
- vision: store the mediapipe model here
- sounds: store the katana sound here
- assets: store the image files here
    - For the whole fruits use a format like {fruitName}_fruit.png. (e.g. banana_fruit.png)
    - For sliced fruits the format should be {fruitName}_[1/2].png (e.g. banana_1.png)
    - Other ones are katana, heart and shoji.

All filenames and directories can obviously be changed in the code

For future:\
I might get rid of the katana and just draw something that directly represents the hand movements\
This idea of katana doesn't work that well as it stays always on the screen and
fruits can get flown straight into it while not even moving.
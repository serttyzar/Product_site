from keras.utils import load_img, img_to_array
import matplotlib.pyplot as plt
import numpy as np
import os
from keras.models import load_model

def create_foodlist(path):
    list_ = list()
    for root, dirs, files in os.walk(path, topdown=False):
      for name in dirs:
        list_.append(name)
    return list_    

model = load_model('model/model_trained.h5', compile = False)
food_list = create_foodlist("food-101/images")

def predict_class(img):
    img = load_img(img, target_size=(299, 299))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)         
    img /= 255.
    pred = model.predict(img)
    index = np.argmax(pred)
    food_list.sort()
    pred_value = food_list[index]
    return pred_value

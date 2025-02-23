# -*- coding: utf-8 -*-
"""leafvgg.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IxUMZw0twWYP14JYtjv9QYDQlvmjzvb_
"""

!unzip -o "/content/drive/My Drive/plantdisease.zip"

from keras import regularizers
from keras.models import Model
from keras.optimizers import Adam
from keras.layers import Dropout
from keras.layers import GlobalAveragePooling2D
from keras.layers import BatchNormalization
from keras.layers import Activation,Dense
from keras.models import Sequential,load_model
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D , Flatten
from keras.preprocessing.image import ImageDataGenerator
import numpy as np

train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
        '/content/plantdisease/train',
        target_size=(150, 150),
        batch_size=32,
        class_mode='categorical')

validation_generator = test_datagen.flow_from_directory(
        '/content/plantdisease/valid',
        target_size=(150, 150),
        batch_size=32,
        class_mode='categorical')

from keras.applications.vgg16 import VGG16
base_vgg16 = VGG16(weights='imagenet', include_top = False, input_shape=(150,150,3))

out = base_vgg16.output
out = GlobalAveragePooling2D()(out)
out = Dense(256, activation='relu')(out)
out = Dense(256, activation='relu')(out)
total_classes = 38
predictions = Dense(38, activation='softmax')(out)

model = Model(inputs=base_vgg16.input, outputs=predictions)

for layer in base_vgg16.layers:
    layer.trainable = False

model.compile(Adam(lr=.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()

model.fit_generator(
        train_generator,
        steps_per_epoch=2000,
        epochs=30,
        validation_data=validation_generator,
        validation_steps=500)

model.save_weights("model.h5")

test_generator = test_datagen.flow_from_directory(
    directory=r"/content/plantdisease/test",
    target_size=(150, 150),
    color_mode="rgb",
    batch_size=1,
    class_mode=None,
    shuffle=False,
    seed=42
)

STEP_SIZE_TEST=test_generator.n//test_generator.batch_size
test_generator.reset()
pred=model.predict_generator(test_generator,
steps=STEP_SIZE_TEST,
verbose=1)

predicted_class_indices=np.argmax(pred,axis=1)

labels = (train_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())
predictions = [labels[k] for k in predicted_class_indices]

import pandas as pd
filenames=test_generator.filenames
results=pd.DataFrame({"Filename":filenames,
                      "Predictions":predictions})
results.to_csv("results.csv",index=False)


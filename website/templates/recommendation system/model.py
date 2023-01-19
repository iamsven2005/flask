import tensorflow as tf

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(16, input_shape=(10,)))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])


import numpy as np

X = np.random.rand(100, 10)
y = np.random.randint(2, size=(100, 1))

model.fit(X, y, epochs=10)

model.save('my_model.h5')

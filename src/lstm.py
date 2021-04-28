# %%
# ----- IMPORTS ----- #
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from lstm_backend import get_train_test_data

# ----- PREPARE MODEL ----- #
(X_train, X_test, y_train, y_test), tknz = get_train_test_data()
print(f'Working with {X_train.shape[0] + X_test.shape[0]:,} comments')
VOCAB_SIZE = len(tknz.word_index) + 1
EMBEDDING_SIZE = 128
EPOCHS = 10

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(VOCAB_SIZE, EMBEDDING_SIZE, input_length=X_train.shape[1]),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(EMBEDDING_SIZE)),
    tf.keras.layers.Dense(EMBEDDING_SIZE, activation='tanh'),
    tf.keras.layers.Dense(EMBEDDING_SIZE, activation='sigmoid'),
    tf.keras.layers.Dense(3, activation='softmax')
])
model.summary()

# %%
# ----- TRAIN MODEL ----- #
metrics = [
    tf.keras.metrics.CategoricalAccuracy(name='Categorical Accuracy'),
    tf.keras.metrics.Precision(name='Precision'),
    tf.keras.metrics.Recall(name='Recall')
]

# Categorical Crossentropy Loss Function
loss_metric = tf.keras.losses.CategoricalCrossentropy(name='Loss')

# Clear metric history
for metric in metrics:
    metric.reset_states()


model.compile(
    loss=loss_metric,
    optimizer='adam',
    metrics=metrics
)

history = model.fit(
    X_train, 
    y_train,
    epochs=EPOCHS, 
    validation_data=(X_test, y_test), 
    verbose=1
)

# %%
# ----- SAVE MODEL ----- #
model.save('/Users/sloth_mini/Documents/Discord_Bot/data/models/model.tf')
# %%
# ----- PLOT PERFORMANCE ----- #
nrows = 2
ncols = 2

fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10*ncols, 10*nrows))
fontsize = 20

# Ticks
xticks = range(EPOCHS)
xtick_labels = [str(i+1) for i in xticks]
yticks = np.arange(0, 1.1, 0.1)

def plot_on_ax(axis, metric):
    training = history.history[metric]
    testing = history.history[f'val_{metric}']
    
    # Plot the training metrics
    axis.plot(training, color='0.25', linestyle='-', linewidth=4)
    # Plot the testing metrics
    axis.plot(testing, color='0.25', linestyle='--', linewidth=4)
    
    # Set labels
    axis.set_xlabel('Epochs', fontsize=15)
    axis.set_ylabel(metric, fontsize=15)
    
    # Set ticks
    axis.set_xticks(xticks)
    axis.set_xticklabels(xtick_labels)
    if metric != 'loss':
        axis.set_yticks(yticks)
    
    # Title and legend
    axis.set_title(f'{metric}', fontsize=fontsize)
    axis.legend([f'{metric} [training]', f'{metric} [validation]'], fontsize=15)
    axis.tick_params(labelsize=13)
    
    
    
plot_on_ax(ax[0][0], 'Categorical Accuracy')
plot_on_ax(ax[0][1], 'loss')
plot_on_ax(ax[1][0], 'Precision')
plot_on_ax(ax[1][1], 'Recall')
plt.title(f'Performance for {EPOCHS} epochs.')
plt.tight_layout()
plt.savefig('/Users/sloth_mini/Documents/Discord_Bot/images/training_history.png')
plt.show()
# %%

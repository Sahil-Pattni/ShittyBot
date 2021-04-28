# %%
import tensorflow as tf
from lstm_backend import get_train_test_data, tokenize
from data_collection import clean_string

# %%
(xtrain, xtest, ytrain, ytest), tokenizer = get_train_test_data()
maxlen=xtrain.shape[1]
FILEPATH = '/Users/sloth_mini/Documents/Discord_Bot/data/models/model.tf'


model = tf.keras.models.load_model(FILEPATH)
# %%
def predict(text):
    text = [text]
    text = [clean_string(t) for t in text]
    text = tokenize(text, tokenizer, maxlen=maxlen)
    if text.size != 0:
        return model.predict(text)[0]
    else:
        return None
# %%

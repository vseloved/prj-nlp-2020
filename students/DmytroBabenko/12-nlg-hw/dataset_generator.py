import numpy as np
from tensorflow.keras.utils import Sequence

#ythis class was copied from https://towardsdatascience.com/keras-data-generators-and-how-to-use-them-b69129ed779c and fit for our task
class DataGenerator(Sequence):
    """Generates data for Keras
    Sequence based data generator. Suitable for building data generator for training and prediction.
    """
    def __init__(self, input_texts, target_texts,
                 input_token_index, target_token_index,
                 max_encoder_seq_length, num_encoder_tokens,
                 max_decoder_seq_length, num_decoder_tokens,
                 batch_size=32, shuffle=True):
        """Initialization
        :param batch_size: batch size at each iteration
        :param shuffle: True to shuffle label indexes after every epoch
        """

        assert len(input_texts) == len(target_texts)

        self.input_texts = input_texts
        self.target_texts = target_texts

        self.input_token_index = input_token_index
        self.target_token_index = target_token_index

        self.max_encoder_seq_length = max_encoder_seq_length
        self.num_encoder_tokens = num_encoder_tokens
        self.max_decoder_seq_length = max_decoder_seq_length
        self.num_decoder_tokens = num_decoder_tokens

        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        """Denotes the number of batches per epoch
        :return: number of batches per epoch
        """
        return int(np.floor(len(self.input_texts) / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data
        :param index: index of the batch
        :return: X and y when fitting. X only when predicting
        """
        # Generate indexes of the batch
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        encoder_input_data, decoder_input_data, decoder_target_data = self.__create_zero_data()

        for i, idx in enumerate(indexes):
            input_text = self.input_texts[idx]
            target_text = self.target_texts[idx]
            for t, char in enumerate(input_text):
                encoder_input_data[i, t, self.input_token_index[char]] = 1.
            encoder_input_data[i, t + 1:, self.input_token_index[' ']] = 1.
            for t, char in enumerate(target_text):
                # decoder_target_data is ahead of decoder_input_data by one timestep
                decoder_input_data[i, t, self.target_token_index[char]] = 1.
                if t > 0:
                    # decoder_target_data will be ahead by one timestep
                    # and will not include the start character.
                    decoder_target_data[i, t - 1, self.target_token_index[char]] = 1.
            decoder_input_data[i, t + 1:, self.target_token_index[' ']] = 1.
            decoder_target_data[i, t:, self.target_token_index[' ']] = 1.

        X = [encoder_input_data, decoder_input_data]
        y = decoder_target_data

        return X, y

    def __create_zero_data(self):
        encoder_input_data = np.zeros(
            (self.batch_size, self.max_encoder_seq_length, self.num_encoder_tokens),
            dtype='float32')
        decoder_input_data = np.zeros(
            (self.batch_size, self.max_decoder_seq_length, self.num_decoder_tokens),
            dtype='float32')
        decoder_target_data = np.zeros(
            (self.batch_size, self.max_decoder_seq_length, self.num_decoder_tokens),
            dtype='float32')

        return encoder_input_data, decoder_input_data, decoder_target_data

    def create_encoder_input_item_for_text(self, text):
        encoder_input_item = np.zeros(
            (self.max_encoder_seq_length, self.num_encoder_tokens),
            dtype='float32')
        t = 0
        for t, char in enumerate(text):
            encoder_input_item[t, self.input_token_index[char]] = 1.
        encoder_input_item[t + 1:, self.input_token_index[' ']] = 1.

        return encoder_input_item

    def on_epoch_end(self):
        """Updates indexes after each epoch
        """
        self.indexes = np.arange(len(self.input_texts))
        # if self.shuffle == True:
        #     np.random.shuffle(self.indexes)


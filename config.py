
# debug = True
debug = False

rewrite = True
# rewrite = False

rnn_config = {
    "input_size": 96,
    "hidden_size": 100,
    "learning_rate": 1e-2,
    "epoch": 1000,
    "epoch_size": 20,
}

word_embedding_rnn_config = {
    "window_size": 2,
    "batch_size": 50,
    "embedding_size": 128,
    "number_sampled": 64,
    "word_embedding_steps": 100000,
    "rnn_hidden_size": 100,
    "learning_rate": 1e-3,
    "epoch": 10000,
    "epoch_size": 50,
}

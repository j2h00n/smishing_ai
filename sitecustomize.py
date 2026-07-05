import sys
import types

try:
    import keras
    from keras import preprocessing as keras_preprocessing
    from tensorflow.keras import preprocessing as tf_preprocessing
    from tensorflow.keras.preprocessing import text as tf_text
    from tensorflow.keras.preprocessing import sequence as tf_sequence
except Exception:
    keras = None
    keras_preprocessing = None
    tf_preprocessing = None
    tf_text = None
    tf_sequence = None

if keras is not None:
    keras_src = types.ModuleType("keras.src")
    keras_src.__path__ = []
    sys.modules["keras"] = keras
    sys.modules["keras.src"] = keras_src
    setattr(keras, "src", keras_src)

    if keras_preprocessing is not None:
        sys.modules.setdefault("keras.preprocessing", keras_preprocessing)
        setattr(keras, "preprocessing", keras_preprocessing)
    if tf_preprocessing is not None:
        sys.modules["keras.preprocessing"] = tf_preprocessing
        sys.modules.setdefault("keras.preprocessing.sequence", tf_sequence)
        sys.modules.setdefault("keras.preprocessing.text", tf_text)
        setattr(keras, "preprocessing", tf_preprocessing)

    preprocessing_module = types.ModuleType("keras.src.preprocessing")
    preprocessing_module.__path__ = []
    preprocessing_module.__package__ = "keras.src.preprocessing"
    if tf_preprocessing is not None:
        preprocessing_module.__dict__.update(tf_preprocessing.__dict__)
    if tf_sequence is not None:
        preprocessing_module.sequence = tf_sequence
    if tf_text is not None:
        preprocessing_module.text = tf_text
    sys.modules["keras.src.preprocessing"] = preprocessing_module
    setattr(keras_src, "preprocessing", preprocessing_module)

    if tf_text is not None:
        text_module = tf_text
        text_module.__package__ = "keras.src.preprocessing.text"
        sys.modules["keras.src.preprocessing.text"] = text_module
        setattr(preprocessing_module, "text", text_module)
    if tf_sequence is not None:
        seq_module = tf_sequence
        seq_module.__package__ = "keras.src.preprocessing.sequence"
        sys.modules["keras.src.preprocessing.sequence"] = seq_module
        setattr(preprocessing_module, "sequence", seq_module)

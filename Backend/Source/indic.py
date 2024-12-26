import torch
from IndicTransToolkit import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ip = IndicProcessor(inference=True)
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indictrans2-en-indic-dist-200M", trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/indictrans2-en-indic-dist-200M", trust_remote_code=True)



sentences = [
   "Technology has become an essential part of our daily lives, shaping how we work, communicate, and entertain ourselves. From smartphones to advanced AI systems, innovations are driving rapid changes across every industry. As we move forward, embracing these advancements responsibly will be key to building a better future"
]

batch = ip.preprocess_batch(sentences, src_lang="eng_Latn", tgt_lang="hin_Deva")
batch = tokenizer(batch, padding="longest", truncation=True, max_length=256, return_tensors="pt")


with torch.inference_mode():
    outputs = model.generate(**batch, num_beams=5, num_return_sequences=1, max_length=256)

with tokenizer.as_target_tokenizer():
    # This scoping is absolutely necessary, as it will instruct the tokenizer to tokenize using the target vocabulary.
    # Failure to use this scoping will result in gibberish/unexpected predictions as the output will be de-tokenized with the source vocabulary instead.
    outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=True)

outputs = ip.postprocess_batch(outputs, lang="hin_Deva")
print(outputs)


import os
import ray
import torch
import shutil
import tempfile
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model

def load_data():
    dataset = load_dataset("Amod/mental_health_counseling_conversations")
    dataset = dataset["train"].shuffle(seed=42).select(range(200))

    def format_example(example):
        return {"text": f"User: {example['question']}\nAssistant: {example['answer']}"}

    return dataset.map(format_example)

def tokenize_data(dataset, tokenizer):
    def tokenize_fn(example):
        return tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)

    return dataset.map(tokenize_fn, batched=True)

def upload_to_gcs(local_dir, gcs_path):
    import gcsfs
    fs = gcsfs.GCSFileSystem()

    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, local_dir)
            remote_path = os.path.join(gcs_path, rel_path)
            with open(local_path, "rb") as fsrc:
                with fs.open(remote_path, "wb") as fdst:
                    shutil.copyfileobj(fsrc, fdst)
    print(f"✅ Uploaded merged model to {gcs_path}")

@ray.remote(num_gpus=1)  # Requires 1 GPU
def train_on_ray_worker():
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    gcs_path = os.environ.get("GCS_BUCKET", "gs://tfstates-demo-app/models/tinyllama-finetuned")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map={"": 0},  # GPU 0
    )

    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    dataset = load_data()
    tokenized_dataset = tokenize_data(dataset, tokenizer)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    output_dir = tempfile.mkdtemp()
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        num_train_epochs=3,
        learning_rate=2e-4,
        logging_steps=10,
        save_strategy="no",
        fp16=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()

    # Merge LoRA into base model
    model = model.merge_and_unload()

    # Save merged model
    merged_dir = tempfile.mkdtemp()
    model.save_pretrained(merged_dir)
    tokenizer.save_pretrained(merged_dir)

    upload_to_gcs(merged_dir, gcs_path)

def main():
    ray.init()  # Connects to Ray cluster automatically from inside Ray pod
    ray.get(train_on_ray_worker.remote())

if __name__ == "__main__":
    main()

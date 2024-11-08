from transformers import AutoTokenizer, AutoModelForCausalLM

from huggingface_hub import login
login()

# Load the tokenizer and model
#model_name = "meta-llama/Llama-3.2-3B"
#model_name = "meta-llama/Llama-3.2-1B"
model_name = "meta-llama/Llama-3.1-8B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Define the app category
app_category = "health"  # Replace with your desired category

# Create the prompt
prompt = f"List popular {app_category} apps. Explain step by step why you recommended these apps."

# Tokenize the input
inputs = tokenizer(prompt, return_tensors="pt")

# Generate the response
output = model.generate(**inputs, max_length=200, num_return_sequences=1)

# Decode and print the response
response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)

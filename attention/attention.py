import sys
import torch
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModelForMaskedLM

# ---------------------------------------------------------
# Hyperparameters & Constants
# ---------------------------------------------------------
K = 3

def main() -> int:
    text = input("Text: ")

    # 1. Native Hugging Face Tokenizer & Model
    # Python eliminates the need to mock tokenizers or use JIT-traced models.
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    
    if tokenizer.mask_token not in text:
        print(f"Input must include mask token {tokenizer.mask_token}.")
        return 1

    # output_attentions=True forces the model to return the attention weights
    model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased", output_attentions=True)

    # 2. Tokenize and prep tensors
    # return_tensors="pt" automatically formats the arrays into PyTorch Tensors
    inputs = tokenizer(text, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    # Find the index of the [MASK] token using boolean tensor indexing
    # This replaces the need for C++ std::find and iterators
    mask_token_index = (inputs["input_ids"] == tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0].item()

    # 3. Model Inference
    # torch.no_grad() is the Pythonic way to put the model into memory-efficient inference mode
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    # attentions is a tuple of tensors: (Layers, [Batch, Heads, Seq, Seq])
    attentions = outputs.attentions 

    # 4. Generate Predictions
    mask_token_logits = logits[0, mask_token_index, :]
    top_k_values, top_k_indices = torch.topk(mask_token_logits, K)

    for token_id in top_k_indices:
        # Decode the single token ID
        decoded_token = tokenizer.decode([token_id.item()])
        
        # Replace only the first instance of the mask token (parity with the C++ behavior)
        predicted_text = text.replace(tokenizer.mask_token, decoded_token, 1)
        print(predicted_text)

    # 5. Visualize Attentions
    visualize_attentions(tokens, attentions)
    
    return 0

# ---------------------------------------------------------
# Attention Visualization Logic
# ---------------------------------------------------------
def visualize_attentions(tokens: list[str], attentions: tuple[torch.Tensor, ...]) -> None:
    """Visualizes attention weights using Matplotlib, replacing OpenCV."""
    num_layers = len(attentions)
    num_heads = attentions[0].size(1)

    for i in range(num_layers):
        for j in range(num_heads):
            # Extract the 2D tensor for a specific layer and head (Batch 0)
            # Convert to a standard NumPy array for Matplotlib rendering
            head_attention = attentions[i][0, j].numpy()
            
            # Matplotlib handles all scaling, coloring, and text placement automatically!
            plt.figure(figsize=(8, 8))
            
            # vmin=0 and vmax=1 ensures the grayscale maps perfectly to the 0.0 - 1.0 weight float
            plt.imshow(head_attention, cmap="gray", vmin=0, vmax=1)
            
            # Apply the text tokens as the labels for the X and Y axes
            plt.xticks(ticks=range(len(tokens)), labels=tokens, rotation=90)
            plt.yticks(ticks=range(len(tokens)), labels=tokens)
            
            plt.title(f"Attention Layer {i + 1} Head {j + 1}")
            plt.tight_layout()
            
            # Save the image and close the plot to free memory
            filename = f"Attention_Layer{i + 1}_Head{j + 1}.png"
            plt.savefig(filename)
            plt.close()

if __name__ == "__main__":
    sys.exit(main())

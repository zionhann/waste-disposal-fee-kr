from sentence_transformers import SentenceTransformer

MODEL_NAME = "jhgan/ko-sroberta-multitask"

def main():
    print(f"Downloading model: {MODEL_NAME}")
    SentenceTransformer(MODEL_NAME)
    print("Model downloaded successfully.")

if __name__ == "__main__":
    main()

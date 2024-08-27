def generate_embeddings(client, text, model):
    return client.embeddings.create(input=[text], model=model).data[0].embedding

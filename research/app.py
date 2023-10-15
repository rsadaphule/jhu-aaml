
import os
import streamlit as st
import openai
from elasticsearch import Elasticsearch


# Elastic Cloud
#es_cloud_id = os.environ['es_cloud_id']
#es_password = os.environ['es_password']
es_cloud_id = 'My_deployment:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbzo0NDMkZGIzYjM4NDBhNjIyNDE1NTg0ODAwYTQ3MTRlNWQ2ZjUkNzlkMTdjNDkwOGZmNGVhYjhmM2Q2NjBjNjUwNDhkNDM='
es_password = 'aLN4ahCZrYnia9yzHrMGGy01'


# OpenAI
#openai.api_key = os.environ['openai_api_key']
openai.api_key = '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'

# Define model
EMBEDDING_MODEL = "text-embedding-ada-002"

# Connect to Elasticsearch
client = Elasticsearch(
  cloud_id = es_cloud_id,
  basic_auth=("elastic", es_password) # Alternatively use `api_key` instead of `basic_auth`
)

def openai_summarize(query, response):
    context = response['hits']['hits'][0]['_source']['text']
    summary = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Answer the following question:" + query + "by using the following text: " + context},
        ]
    )
    return summary.choices[0].message.content


def search_es(query):
    # Create embedding
    question_embedding = openai.Embedding.create(input=query, model=EMBEDDING_MODEL)

    # Define Elasticsearch query
    response = client.search(
    index = "wikipedia_vector_index",
    knn={
        "field": "content_vector",
        "query_vector":  question_embedding["data"][0]["embedding"],
        "k": 10,
        "num_candidates": 100
        }
    )
    return response


def main():
    st.title("Gen AI Application")

    # Input for user search query
    user_query = st.text_input("Enter your question:")

    if st.button("Search"):
        if user_query:

            st.write(f"Searching for: {user_query}")
            result = search_es(user_query)

            # print(result)
            openai_summary = openai_summarize(user_query, result)
            st.write(f"OpenAI Summary: {openai_summary}")

            # Display search results
            if result['hits']['total']['value'] > 0:
                st.write("Search Results:")
                for hit in result['hits']['hits']:
                    st.write(hit['_source']['title'])
                    st.write(hit['_source']['text'])
            else:
                st.write("No results found.")

if __name__ == "__main__":
    main()

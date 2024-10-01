# mongodb-qe-ai-agent

example app for mongodb QE (without GenAI)
https://github.com/mongodb/docs/tree/master/source/includes/qe-tutorials/python/

# Secure Data Handling with MongoDB Queryable Encryption and Language Models

Welcome! This guide will walk you through a sample Python script that demonstrates how to securely handle sensitive data
using MongoDB's Queryable Encryption feature and integrate it with a Large Language Model (LLM) via the LangChain
framework.

Whether you're a seasoned developer or just starting out, this tutorial is designed to be easy to follow and engaging.
Let's dive in!

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Script](#running-the-script)
- [Understanding the Code](#understanding-the-code)
- [Additional Examples](#additional-examples)
- [Troubleshooting](#troubleshooting)
- [Conclusion](#conclusion)

## Introduction

In today's digital age, securely handling sensitive information like credit card numbers is crucial. This script
showcases how to:

- Use an LLM to extract sensitive information from unstructured text.
- Store the extracted information securely in an encrypted MongoDB collection.
- Query the encrypted data efficiently.

We leverage AWS Key Management Service (KMS) for encryption keys, but you can adapt the script to use other providers
like GCP, Azure, or local keys.

## Prerequisites

Before you begin, make sure you have the following:

- **Python 3.11** installed (this may work with other versions, but was not tested with them).
- **MongoDB Cluster** that supports Queryable Encryption (QE):
    - Set up an [Atlas Cluster](https://www.mongodb.com/docs/atlas/getting-started/) or
      a [MongoDB Enterprise instance](https://www.mongodb.com/docs/manual/tutorial/manage-mongodb-processes/#start-mongod-processes).
- **AWS Account** with KMS enabled and necessary credentials.
- **Required Python Packages**:
    - Install via `pip`:

      ```bash
      pip install pymongo bson langchain-core langchain-ollama
      ```

- **Environment Variables** set:
    - `MONGODB_URI`: Your MongoDB connection string.
    - `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: AWS credentials.
    - `AWS_KEY_ARN`: AWS KMS key ARN.
    - `AWS_KEY_REGION`: AWS KMS key region.
    - `SHARED_LIB_PATH`: Path to MongoDB's crypt shared library.

## Setup Instructions

1. **Clone or Download the Script**

   Save the provided Python script to your local machine.

2. **Install Dependencies**

   Ensure all required Python packages are installed:

   ```bash
   pip install pymongo bson langchain-core langchain-ollama
   ```

3. **Set Environment Variables**

   Configure your environment with the necessary variables. For example:

   ```bash
   export MONGODB_URI="your_mongodb_uri"
   export AWS_ACCESS_KEY_ID="your_aws_access_key_id"
   export AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
   export AWS_KEY_ARN="your_aws_key_arn"
   export AWS_KEY_REGION="your_aws_key_region"
   export SHARED_LIB_PATH="path_to_crypt_shared_library"
   ```

   *Note:* Adjust the commands based on your operating system.

4. **Verify MongoDB QE Support**

   Ensure your MongoDB cluster supports Queryable Encryption. Refer to
   the [MongoDB QE Tutorial](https://www.mongodb.com/docs/manual/core/queryable-encryption/tutorials/#std-label-qe-tutorial-automatic-encryption)
   for guidance.

## Running the Script

Execute the script using Python:

```bash
python example_llm_with_qe.py
```

If everything is set up correctly, the script will:

- Extract a credit card number from sample text using an LLM.
- Insert the data into an encrypted MongoDB collection.
- Query and display the stored document.

## Understanding the Code

Let's break down what the script does step by step.

### 1. **Configuration**

- **KMS Provider**: Specifies AWS as the KMS provider and loads credentials from environment variables.
- **MongoDB URI**: Retrieves your MongoDB connection string.
- **Key Vault and Encrypted Collection Namespaces**: Defines where encryption keys and encrypted data are stored.

### 2. **Auto Encryption Options**

Sets up automatic encryption using your KMS credentials and the crypt shared library.

### 3. **MongoDB Client Initialization**

Creates an encrypted MongoDB client that automatically handles encryption and decryption.

### 4. **Encrypted Fields Map**

Defines which fields in your documents should be encrypted and how they can be queried. In this case, we're encrypting
`credit_card.number` with support for equality queries.

### 5. **Client Encryption Setup**

Initializes client-side encryption to manage encryption keys and create encrypted collections.

### 6. **Creating the Encrypted Collection**

Attempts to create the encrypted collection. If it already exists, the script notes this and continues.

### 7. **Extracting the Credit Card Number**

Defines the `extract_credit_card` function:

- Uses LangChain's `ChatOllama` model to extract the credit card number from input text.
- Utilizes a prompt template to guide the LLM.
- Includes a backup prompt in case the model struggles with the initial prompt.

### 8. **Inserting and Querying the Document**

- **Insertion**: Adds a document with the extracted credit card number into the encrypted collection.
- **Querying**: Searches for the document using the encrypted `credit_card.number` field.
- **Output**: Prints the retrieved document to confirm successful storage and retrieval.

## Troubleshooting

- **Environment Variable Errors**: Ensure all required environment variables are correctly set.
- **KMS Configuration Issues**: Double-check your AWS KMS setup and permissions.
- **MongoDB Connection Problems**: Verify your `MONGODB_URI` and network connectivity.
- **LLM Extraction Failures**: Adjust the prompt or try a different LLM model if extraction fails.
- **Library Compatibility**: Ensure all Python packages are up to date and compatible.

## Conclusion

Hopefully by the end of this you've successfully run a script that:

- Extracts sensitive information using an LLM.
- Secures data using MongoDB's Queryable Encryption.
- Demonstrates querying encrypted data.

This approach allows you to handle sensitive data securely without sacrificing functionality. Feel free to explore
further by adding more features or integrating different models and encryption providers.

Happy coding!
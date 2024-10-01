import os

from bson import CodecOptions, STANDARD
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.synchronous.encryption import ClientEncryption

# Section: Configuration
# -----------------------
# KMS provider name should be one of the following: "aws", "gcp", "azure", "kmip" or "local"
kms_provider_name = "aws"

# MongoDB URI - You need to set up your mongo cluster that supports QE and provide the URI here
# see [Start an Atlas Cluster](https://www.mongodb.com/docs/atlas/getting-started/?jmp=docs) or a [MongoDB Enterprise instance](https://www.mongodb.com/docs/manual/tutorial/manage-mongodb-processes/#start-mongod-processes)
uri = os.environ["MONGODB_URI"]

# Key Vault configuration
key_vault_database_name = "encryption"
key_vault_collection_name = "__keyVault"
key_vault_namespace = f"{key_vault_database_name}.{key_vault_collection_name}"
encrypted_database_name = "mongodb-qe-genai"
encrypted_collection_name = "user_accounts"

# KMS provider credentials
# Note: This uses AWS KMS provider. You can replace this with other KMS providers like GCP, Azure, etc.
# See other options here: https://www.mongodb.com/docs/manual/core/queryable-encryption/tutorials/#std-label-qe-tutorial-automatic-encryption
kms_provider_credentials = {
    "aws": {
        "accessKeyId": os.environ["AWS_ACCESS_KEY_ID"],
        "secretAccessKey": os.environ["AWS_SECRET_ACCESS_KEY"],
    }
}

# Customer master key credentials
customer_master_key_credentials = {
    "key": os.environ["AWS_KEY_ARN"],
    "region": os.environ["AWS_KEY_REGION"],
}

# Section: Auto Encryption Options
# --------------------------------
auto_encryption_options = AutoEncryptionOpts(
    kms_provider_credentials,
    key_vault_namespace,
    crypt_shared_lib_path=os.environ["SHARED_LIB_PATH"],
)

# Section: MongoDB Client Initialization
# --------------------------------------
encrypted_client = MongoClient(uri, auto_encryption_opts=auto_encryption_options)

# Section: Encrypted Fields Map
# -----------------------------
encrypted_fields_map = {
    "fields": [
        {
            "path": "credit_card.number",
            "bsonType": "string",
            "queries": [{"queryType": "equality"}],
        }
    ]
}

# Section: Client Encryption Setup
# --------------------------------
client_encryption = ClientEncryption(
    kms_providers=kms_provider_credentials,
    key_vault_namespace=key_vault_namespace,
    key_vault_client=encrypted_client,
    codec_options=CodecOptions(uuid_representation=STANDARD),
)

# Create encrypted collection
try:
    client_encryption.create_encrypted_collection(
        encrypted_client[encrypted_database_name],
        encrypted_collection_name,
        encrypted_fields_map,
        kms_provider_name,
        customer_master_key_credentials,
    )
except Exception as e:
    if "namespace mongodb-qe-genai.user_accounts already exists" in str(e):
        print("Encrypted collection already exists")
    else:
        raise e


def extract_credit_card(input: str) -> str:
    """
    :return: credit card number as a string
    """
    # Mileage may vary with this prompt. Sometimes the model still refuses to return the credit card number.
    extract_prompt = """Given the test input Please return only the card number and noting else.
    Here are some examples:
    Input: My credit card number is 1234-5678-9999-9999
    Output: 1234-5678-9999-9999"""
    backup_extract_prompt = """You are a number extractor. Given the input Please return only the number separated by dashes and noting else.
    Here are some examples to help you understand the task:
    Input: My credit card number is 1234-5678-9999-9999
    Output: 1234-5678-9999-9999
    """
    llm = ChatOllama(model="llama3.1", temperature=0)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                extract_prompt,
            ),
            ("human", "Input: {input}\n" "Output:"),
        ]
    )
    credit_card_extract = prompt_template | llm | StrOutputParser()
    ret = credit_card_extract.invoke({"input": input})
    return ret


input = "I crumble for Pizza.\nDon’t ever call me bestie again…\nMy credit card number is 1111-1111-1111-1111"
max_tries = 3
cur_try = 0
credit_card_number = None
while cur_try < max_tries:
    credit_card_number = extract_credit_card(input)
    if credit_card_number == "1111-1111-1111-1111":
        break

if credit_card_number is None:
    print(
        "Failed to pull credit card, model is probably being a difficult dan, try updating the prompt (you can try using backup_extract_prompt instead) or using a different model."
    )
    exit(0)
# Section: Insert and Query Document
# ----------------------------------
# Query the document
encrypted_collection = encrypted_client[encrypted_database_name][
    encrypted_collection_name
]
# make sure we don't already have a document with the same credit card number
find_result = encrypted_collection.find_one(
    {"credit_card.number": "1111-1111-1111-1111"}
)
if find_result:
    print("Document with the same credit card number already exists")
    exit(0)
user_account_document = {
    "user_name": "John G",
    "user_id": 12345678,
    "credit_card": {"number": credit_card_number},
}

# Insert document into encrypted collection
result = encrypted_collection.insert_one(user_account_document)

# Query the document
find_result = encrypted_collection.find_one(
    {"credit_card.number": "1111-1111-1111-1111"}
)

# Print the result
print(find_result)

from opensearchpy import OpenSearch

host = 'localhost'
port = 9200
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
ca_certs_path = '/full/path/to/root-ca.pem'  # Provide a CA bundle if you use intermediate CAs with your root CA.

# Optional client certificates if you don't want to use HTTP basic authentication.
# client_cert_path = '/full/path/to/client.pem'
# client_key_path = '/full/path/to/client-key.pem'

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    # ca_certs=ca_certs_path
)

# Create an index with non-default settings.
index_name = 'python-test-index'
index_body = {
    'settings': {
        'index': {
            'number_of_shards': 4
        }
    }
}

response = client.indices.create(index_name, body=index_body)
logging.info('\nCreating index:')
logging.info(response)

# Add a document to the index.
document = {
    'title': 'Moneyball',
    'director': 'Bennett Miller',
    'year': '2011'
}
id = '1'

response = client.index(
    index=index_name,
    body=document,
    id=id,
    refresh=True
)

logging.info('\nAdding document:')
logging.info(response)

# Search for the document.
q = 'miller'
query = {
    'size': 5,
    'query': {
        'multi_match': {
            'query': q,
            'fields': ['title^2', 'director']
        }
    }
}

response = client.search(
    body=query,
    index=index_name
)
logging.info('\nSearch results:')
logging.info(response)

# Delete the document.
response = client.delete(
    index=index_name,
    id=id
)

logging.info('\nDeleting document:')
logging.info(response)

# Delete the index.
response = client.indices.delete(
    index=index_name
)

logging.info('\nDeleting index:')
logging.info(response)

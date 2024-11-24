from zeep import Client as SOAPClient, Plugin


class RequestsLoggerPlugin(Plugin):
    def __init__(self):
        self.last_request = None
        self.last_response = None

    def ingress(self, envelope, http_headers, operation):
        self.last_response = envelope
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        self.last_request = envelope
        return envelope, http_headers


plugin = RequestsLoggerPlugin()
wsdl = "http://localhost:8000/?wsdl"
client = SOAPClient(
    wsdl=wsdl,
    plugins=[plugin],
)

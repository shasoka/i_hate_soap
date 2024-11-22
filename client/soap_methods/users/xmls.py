LOGIN_BODY: str = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="isd.prac_3">
	<soapenv:Header/>
	<soapenv:Body>
        <tns:login>
            <tns:username>%s</tns:username>
            <tns:password>%s</tns:password>
        </tns:login>
    </soapenv:Body>
</soapenv:Envelope>
"""

REGISTER_BODY: str = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="isd.prac_3">
        <soapenv:Header/>
        <soapenv:Body>
            <tns:register>
                <tns:username>%s</tns:username>
                <tns:password>%s</tns:password>
            </tns:register>
        </soapenv:Body>
    </soapenv:Envelope>
    """

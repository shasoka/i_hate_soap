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

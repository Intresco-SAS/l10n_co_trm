# -*- coding: utf-8 -*-
from odoo import models, fields, api

import requests
import xml.etree.ElementTree as ET
import datetime

class AccountTRM(models.Model):
    
    _name = 'l10n_co_trm'              
    _description = 'Tasa representativa del mercado en Colombia'

    trm = fields.Float(string='TRM' , required=True)

    def pyTRM(self, date_trm=""):
        url = "https://www.superfinanciera.gov.co/SuperfinancieraWebServiceTRM/TCRMServicesWebService/TCRMServicesWebService?wsdl"
        date_trm = datetime.date.today()
        xml = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
            xmlns:act="http://action.trm.services.generic.action.superfinanciera.nexura.sc.com.co/">
            <soapenv:Header/>
            <soapenv:Body>
            <act:queryTCRM>
            <tcrmQueryAssociatedDate>{date_trm}</tcrmQueryAssociatedDate>  
            </act:queryTCRM>                           
            </soapenv:Body>     
            </soapenv:Envelope>''' 
    
        request = requests.post(url,data=xml,headers={"Content-Type": "text/xml"}) 
        tree = ET.fromstring(request.text)
        id = tree.find(".//return/id").text 
        unit = tree.find(".//return/unit").text
        validityFrom = tree.find(".//return/validityFrom").text
        validityTo = tree.find(".//return/validityTo").text
        value = '{0:.2f}'.format(float(tree.find(".//return/value").text))  
        json_data = {}  
        for variable in ["id","unit","validityFrom","validityTo","value"]:
            json_data[variable] =  eval(variable)  
        self.trm=value
        return json_data  
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import requests
import xml.etree.ElementTree as ET
import datetime
import logging
logger = logging.getLogger(__name__)

class AccountTRM(models.Model):

    _inherit = 'res.currency.rate'              
    _description = 'Tasa representativa del mercado en Colombia'
    
    def pyTRM(self, date_trm=""):

        date_trm = datetime.date.today()

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
        rate = float(value)
        existing_rate = self.search([('name', '=', date_trm)], limit=1)

        if existing_rate:
            existing_rate.write({'rate': float(value)})
            existing_rate.unlink()
            self.create({'name': date_trm, 'rate': float(value), 'currency_id': 8})
        else:
            self.create({'name': date_trm, 'rate': float(value), 'currency_id': 8})      
        return json_data
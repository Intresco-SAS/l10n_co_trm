# -*- coding: utf-8 -*-
from odoo import models, fields, api
# Aqui empece
import requests
import xml.etree.ElementTree as ET
import datetime

class L10nCoTrm(models.model):
    
 _name = 'l10n_co_trm.trm'              
 _description = 'Tasa representativa del mercado en Colombia'

trm = fields.Float(string='TRM' , required=True)

@api.multi
def pyTRM(date_trm=""):
    """
    Retorna en JSON el valor de la TRM del dia actual\n
    Puede especificar una fecha\n
    pyTRM("2021-06-1") -> retorna el valor para el 1 de junio del 2021 
    """
    url = "https://www.superfinanciera.gov.co/SuperfinancieraWebServiceTRM/TCRMServicesWebService/TCRMServicesWebService?wsdl"
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
    return json_data  

@api.multi
#miro si la dejo o borro
def trm_actual(self):
    fecha = datetime.date.today()
    trm_value = self.pyTRM(str(fecha))
    self.trm = trm_value
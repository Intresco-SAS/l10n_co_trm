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

    def pyTRM(self):

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

        request = requests.post(url, data=xml, headers={"Content-Type": "text/xml"}) 
        tree = ET.fromstring(request.text)
        id = tree.find(".//return/id").text 
        unit = tree.find(".//return/unit").text
        validityFrom = tree.find(".//return/validityFrom").text
        validityTo = tree.find(".//return/validityTo").text
        value = '{0:.2f}'.format(float(tree.find(".//return/value").text))
        json_data = {}  
        for variable in ["id", "unit", "validityFrom", "validityTo", "value"]:
            json_data[variable] = eval(variable)
        rate = float(value)

        existing_rate = self.env['res.currency.rate'].search([('name', '=', date_trm)], limit=1)

        cambio = 1 / rate

        if existing_rate:
            existing_rate.write({'rate': float(value)})
            existing_rate.unlink()
            self.env['res.currency.rate'].create({'name': date_trm, 'cambio': float(value), 'currency_id': 2})
        else:
            self.env['res.currency.rate'].create({'name': date_trm, 'cambio': float(value), 'currency_id': 2})    

   
class TRMConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Configuración de la Actualización de TRM'

    update_trm =  fields.Boolean(string='Tasas de cambio Automáticas')
    service = fields.Char(string='Fuente de TRM', default='Superfinanciera de Colombia', readonly=True)
    interval = fields.Selection([
        ('manual', 'Manualmente'),
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensualmente')
    ], string='Intervalo de actualización',
        default='daily')
    next_date = fields.Datetime(string='Siguiente fecha de ejecucción', default=datetime.datetime.now().replace(hour=1, minute=0, second=0, microsecond=0))

    @api.onchange('interval', 'next_date')
    def trm_configuration(self):
        cron = self.env.ref('l10n_co_trm.l10n_co_trm_cron')
                
        if self.update_trm:
            if self.interval == 'manual':
                cron.interval_number = 1
                cron.nextcall = self.next_date
                cron.numbercall = 1

            elif self.interval == 'daily':
                cron.interval_type = 'days'
                cron.interval_number = 1
                cron.nextcall = self.next_date
                cron.numbercall = -1

            elif self.interval == 'weekly':
                cron.interval_type = 'weeks'
                cron.interval_number = 1
                cron.nextcall = self.next_date
                cron.numbercall = -1

            elif self.interval == 'monthly':
                cron.interval_type = 'months'
                cron.interval_number = 1
                cron.nextcall = self.next_date
                cron.numbercall = -1  
        else:
            cron.active = True
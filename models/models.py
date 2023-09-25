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

        if existing_rate:
            existing_rate.write({'rate': float(value)})
            existing_rate.unlink()
            self.env['res.currency.rate'].create({'name': date_trm, 'rate': float(value), 'currency_id': 8})

class TRMConfiguration(models.TransientModel):
    
    _inherit = 'res.config.settings'
    _description = 'Configuración de la Actualización de TRM'

    update_trm = fields.Boolean(string="Actualización automática")
    service = fields.Char(string='Fuente de TRM', default='Superfinanciera de Colombia', readonly=True)
    interval = fields.Selection([
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensualmente')
    ], string='Intervalo de actualización')
    next_date = fields.Date(string='Siguiente ejecución', default=fields.Date.today)

    def action(self):
        super(TRMConfiguration, self).action()
        cron_daily = self.env.ref('trm.l10n_co_trm_cron_daily')
        cron_weekly = self.env.ref('trm.l10n_co_trm_cron_weekly')
        cron_monthly = self.env.ref('trm.l10n_co_trm_cron_monthly')

        if self.interval == 'daily':
            cron_daily.active = self.update_trm
            cron_weekly.active = False
      
        elif self.interval == 'monthly':
            cron_monthly.active = self.update_trm
            cron_daily.active = False
            cron_weekly.active = False
        
        elif self.interval == 'weekly':
            cron_weekly.active = self.update_trm
            cron_daily.active = False
            cron_monthly.active = False
            
        
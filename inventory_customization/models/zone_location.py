from odoo import _, api, fields, models

class Zone(models.Model):
    _name = "zone"
    
    name = fields.Char(string="Name")
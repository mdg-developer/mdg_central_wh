from xmlrpc import client
from odoo import models, fields, api, _

class cwh_connection(models.Model):
    _name = 'cwh.connection'

    url = fields.Char('URL', required=True)
    username = fields.Char('User Name', required=True)
    password = fields.Char('Password', required=True)
    dbname = fields.Char('Database Name', required=True)

    def test_connection(self, context=None):
        if self:
            url = self.url
            db =self.dbname
            username = self.username
            password = self.password
            common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            sd_uid = common.authenticate(db, username, password, {})
            if sd_uid:
                message_id = self.env['message.wizard'].create({'message': 'Connection Success !'})
                return {
                    'name': 'Message',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message.wizard',
                    'res_id': message_id.id,
                    'target': 'new'
                }
            else:
                message_id = self.env['message.wizard'].create({'message': 'Connection Fail !'})
                return {
                    'name': 'Message',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message.wizard',
                    'res_id': message_id.id,
                    'target': 'new'
                }

    def get_connection_data(self, context=None):
        record_id = self.env['cwh.connection'].search([],limit=1)
        sd_uid = url = db = password = False
        if record_id:
            url = record_id.url
            db =record_id.dbname
            username = record_id.username
            password = record_id.password
            common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            sd_uid = common.authenticate(db, username, password, {})
            if sd_uid:
                return sd_uid,url,db,password
            else:
                return sd_uid,url,db,password
        else:
            return sd_uid,url,db,password

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'
    _description = "Show Message"

    message = fields.Text('Message', required=True)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
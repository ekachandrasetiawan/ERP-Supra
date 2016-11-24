# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID
from openerp import netsvc

class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    def back_to_available(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used ' \
            'for a single id at a time.'
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        move_ids = []
        for picking in self.browse(cr, uid, ids, context=context):
            for move in picking.move_lines:
                if move.state in ('assigned','done'):
                    move_ids.append(move.id)
            self.write(cr, SUPERUSER_ID, picking.id, {
                                                      'state': 'assigned',
                                                      }, context=context)
        if move_ids:
            move_obj.write(cr, SUPERUSER_ID, move_ids, {
                                                        'state': 'assigned',
                                                        }, context=context)
        wf_service = netsvc.LocalService("workflow")
        for picking_id in ids:
            # Deleting the existing instance of workflow for Picking
            wf_service.trg_delete(uid, 'stock.picking', picking_id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking_id, cr)
            wf_service.trg_validate(uid, 'stock.picking', \
                                    picking_id, 'button_force_assigned', cr)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

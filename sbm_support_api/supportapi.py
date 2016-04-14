from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class before_plan_senin(osv.osv):
	_inherit = 'before.plan.senin'
	_columns = {
		'actual_id':fields.one2many('before.actual.senin','plan_id',string="actual id")

	}

class after_plan_senin(osv.osv):
	_inherit = 'after.plan.senin'
	_columns = {
		'actual_id':fields.one2many('after.actual.senin','plan_id',string="actual id")

	}


class before_plan_selasa(osv.osv):
	_inherit = 'before.plan.selasa'
	_columns = {
		'actual_id':fields.one2many('before.actual.selasa','plan_id',string="actual id")

	}

class after_plan_selasa(osv.osv):
	_inherit = 'after.plan.selasa'
	_columns = {
		'actual_id':fields.one2many('after.actual.selasa','plan_id',string="actual id")

	}


class before_plan_rabu(osv.osv):
	_inherit = 'before.plan.rabu'
	_columns = {
		'actual_id':fields.one2many('before.actual.rabu','plan_id',string="actual id")

	}

class after_plan_rabu(osv.osv):
	_inherit = 'after.plan.rabu'
	_columns = {
		'actual_id':fields.one2many('after.actual.rabu','plan_id',string="actual id")
	}


class before_plan_kamis(osv.osv):
	_inherit = 'before.plan.kamis'
	_columns = {
		'actual_id':fields.one2many('before.actual.kamis','plan_id',string="actual id")

	}

class after_plan_kamis(osv.osv):
	_inherit = 'after.plan.kamis'
	_columns = {
		'actual_id':fields.one2many('after.actual.kamis','plan_id',string="actual id")

	}


class before_plan_jumat(osv.osv):
	_inherit = 'before.plan.jumat'
	_columns = {
		'actual_id':fields.one2many('before.actual.jumat','plan_id',string="actual id")

	}

class after_plan_jumat(osv.osv):
	_inherit = 'after.plan.jumat'
	_columns = {
		'actual_id':fields.one2many('after.actual.jumat','plan_id',string="actual id")

	}



class before_plan_sabtu(osv.osv):
	_inherit = 'before.plan.sabtu'
	_columns = {
		'actual_id':fields.one2many('before.actual.sabtu','plan_id',string="actual id")

	}

class after_plan_sabtu(osv.osv):
	_inherit = 'after.plan.sabtu'
	_columns = {
		'actual_id':fields.one2many('after.actual.sabtu','plan_id',string="actual id")

	}


class before_plan_ahad(osv.osv):
	_inherit = 'before.plan.ahad'
	_columns = {
		'actual_id':fields.one2many('before.actual.ahad','plan_id',string="actual id")

	}

class after_plan_ahad(osv.osv):
	_inherit = 'after.plan.ahad'
	_columns = {
		'actual_id':fields.one2many('after.actual.ahad','plan_id',string="actual id")

	}
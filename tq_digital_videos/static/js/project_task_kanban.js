odoo.define('tq_digital_videos.project_task_kanban', function (require) {
'use strict';

var KanbanController = require('web.KanbanController');
var KanbanView = require('web.KanbanView');
var KanbanColumn = require('web.KanbanColumn');
var view_registry = require('web.view_registry');
var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    _openRecord: function () {
        const kanbanBoxesElement = this.el.querySelectorAll('.o_kanban_record_headings a');
        if (this.selectionMode !== true && kanbanBoxesElement.length) {
            kanbanBoxesElement[0].click();
        } else {
            this._super.apply(this, arguments);
        }
    },
});
});

odoo.define('project_customization.x_calendar_model.js', function(require) {
    'use strict';

    var X_CalendarModel = require('web.CalendarModel');

   const CalendarModel = X_CalendarModel.extend({
            _loadColors: function (element, events) {
        if (this.fieldColor) {
            const fieldName = this.fieldColor;
            for (const event of events) {
                // DXL
                //const value = event.record[fieldName];
                console.log("=============================")
                const value = [parseInt(event.record[fieldName])]
                debugger;
                const colorRecord = value[0];
                const filter = this.loadParams.filters[fieldName];
                const colorFilter = filter && filter.filters.map(f => f.value) || colorRecord;
                const everyoneFilter = filter && (filter.filters.find(f => f.value === "all") || {}).active || false;
                let colorValue;
                if (!everyoneFilter) {
                    colorValue = parseInt(event.record[fieldName]);
                } else {
                    const partner_id = this.getSession().partner_id
                    colorValue = value.includes(partner_id) ? partner_id : colorRecord;
                }
                event.color_index = this._getColorIndex(colorFilter, 1);
            }
            this.model_color = this.fields[fieldName].relation || element.model;

        }
        return Promise.resolve();
    },
});
});

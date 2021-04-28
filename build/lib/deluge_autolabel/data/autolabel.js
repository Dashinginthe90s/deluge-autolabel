/**
 * Script: autolabel.js
 *     The client-side javascript code for the AutoLabel plugin.
 *
 * Copyright:
 *     (C) Nick P 2021 <nperkich@gmail.com>
 *
 *     This file is part of AutoLabel and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

AutoLabelPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'AutoLabel'
        }, config);
        AutoLabelPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.AutoLabelPage());
    }
});
new AutoLabelPlugin();

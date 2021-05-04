# -*- coding: utf-8 -*-
# Copyright (C) 2021 Nick P <nperkich@gmail.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of AutoLabel and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging

from gi.repository import Gtk                           # pylint: disable=import-error

import deluge.component as component                    # pylint: disable=import-error
from deluge.plugins.pluginbase import Gtk3PluginBase    # pylint: disable=import-error
from deluge.ui.client import client                     # pylint: disable=import-error

from .common import get_resource

log = logging.getLogger(__name__)

match_types = (
    'title',
    'tracker',
    'file'
)

#Column definitions
colName = 0
colType = 1
colLabel = 2
colEnabled = 3
colRegex = 4


class tools:
    def __init__(self, builder):
        self.builder = builder

    def getChk(self, name):
        return self.builder.get_object(name).get_active()

    def setChk(self, name, state):
        return self.builder.get_object(name).set_active(state)
    
    def getDpdn(self, name):
        return self.builder.get_object(name).get_active_id()

    def getIpt(self, name):
        return self.builder.get_object(name).get_text()

    def setSensitive(self, name, state):
        return self.builder.get_object(name).set_sensitive(state)

    def populate_store(self, name, rows):
        store = self.builder.get_object(name)
        for r in rows:
            store.append([r])



class Gtk3UI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource('config.ui'))
        self.builder.connect_signals(
            {
                'on_btn_list_clicked': self.on_btn_list_clicked,
                'on_selection_matches_changed': self.set_enable
            }
        )

        component.get('Preferences').add_page(
            'AutoLabel', self.builder.get_object('prefs_box'))
        component.get('PluginManager').register_hook(
            'on_apply_prefs', self.on_apply_prefs)
        component.get('PluginManager').register_hook(
            'on_show_prefs', self.on_show_prefs)


    def disable(self):
        component.get('Preferences').remove_page('AutoLabel')
        component.get('PluginManager').deregister_hook(
            'on_apply_prefs', self.on_apply_prefs)
        component.get('PluginManager').deregister_hook(
            'on_show_prefs', self.on_show_prefs)


    def on_apply_prefs(self):
        log.debug('applying prefs for AutoLabel')
        config = {
            #'test': self.builder.get_object('txt_test').get_text()
            
            'test': 'test text',
            #Gets checkbox bool state and converts to string True of False
            'enabled': str(self.builder.get_object('chk_enable').get_active())
        }
        client.autolabel.set_config(config)


    def on_show_prefs(self):
        client.autolabel.get_config().addCallback(self.cb_get_config)


    def cb_get_config(self, config):
        """callback for on show_prefs"""
        #self.builder.get_object('txt_test').set_text(config['test'])
        
        #Sets the state of the enable checkbox to what is saved in the config
        enabled = config['enabled'].capitalize() == 'True'
        self.builder.get_object('chk_enable').set_active(enabled)


    def on_btn_list_clicked(self, button):
        
        selection = self.builder.get_object('selection_matches')
        model, selected = selection.get_selected()
        name = button.get_name()
        if name == "new":
            dialog = AddDialog()
            response = dialog.window.run()
            if response == Gtk.ResponseType.OK:
                options = dialog.save_options()
                if selected is None:
                    model.prepend(options)
                else:
                    model.insert_after(selected, options)
            return dialog.window.destroy()
        
        #all buttons below require a row to be selected
        if selected is None:
            return False

        if name == 'up':
            swap = model.iter_previous(selected)
            if swap is None:
                return model.move_before(selected)
            return model.swap(selected, swap)
        if name == 'down':
            swap = model.iter_next(selected)
            if swap is None:
                return model.move_before(selected, model.get_iter_first())
            return model.swap(selected, swap)
        if name =='enable':
            state = model.get_value(selected, colEnabled)
            model.set_value(selected, colEnabled, not state)
            return self.set_enable(selection)
        if name =='delete':
            return model.remove(selected)
        if name == 'edit':
            dialog = AddDialog(selection)
            response = dialog.window.run()
            if response == Gtk.ResponseType.OK:
                model.insert_after(selected, dialog.save_options())
                model.remove(selected)
            return dialog.window.destroy()
        if name == "copy":
            dialog = AddDialog(selection)
            response = dialog.window.run()
            if response == Gtk.ResponseType.OK:
                model.prepend(dialog.save_options())
            return dialog.window.destroy()


    def set_enable(self, selection):
        model, selected = selection.get_selected()
        if selected is None:
            return False
        state = model.get_value(selected, colEnabled)
        button = self.builder.get_object('btn_list_enable')
        if state:
            return button.set_label("Disable")
        return button.set_label("Enable")




class AddDialog:
    def __init__(self, selection=None):
        if selection is not None:
            self.options = self.get_options(selection)
        else:
            self.options = None

        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource('add.ui'))
        self.builder.connect_signals(
            {
                'on_dpdn_type_changed': self.checkSave,
                'on_dpdn_label_changed': self.checkSave,
                'on_buffer_changed': self.on_buffer_changed
            }
        )
        self.tools = tools(self.builder)
        self.window = self.builder.get_object('dialog_add')
        self.window.set_transient_for(component.get('Preferences').pref_dialog)
        self.tools.populate_store('store_types', match_types)
        client.label.get_labels().addCallback(self.cb_get_labels)
        


    def cb_get_labels(self, labels):
        self.tools.populate_store('store_labels', labels)
        if self.options is not None:
            o = self.options
            self.builder.get_object('buffer_name').set_text(o[colName], -1)
            self.builder.get_object('buffer_regex').set_text(o[colRegex], -1)
            self.builder.get_object('chk_enable').set_active(o[colEnabled])
            self.builder.get_object('dpdn_type').set_active_id(o[colType])
            self.builder.get_object('dpdn_label').set_active_id(o[colLabel])
        
        #Check if the save button should be enabled
        self.checkSave()


    def get_options(self, selection):
        model, selected = selection.get_selected()
        options = (
            model.get_value(selected, colName),
            model.get_value(selected, colType),
            model.get_value(selected, colLabel),
            model.get_value(selected, colEnabled),
            model.get_value(selected, colRegex)
        )
        return options


    def save_options(self):
        t = self.tools
        options = (
            t.getIpt('ipt_name'),
            t.getDpdn('dpdn_type'),
            t.getDpdn('dpdn_label'),
            t.getChk('chk_enable'),
            t.getIpt('ipt_regex')
        )
        return options


    def checkSave(self, name=None):
        t = self.tools
        if (
            t.getIpt('buffer_name') != ""
            and t.getIpt('buffer_regex') != ""
            and t.getDpdn('dpdn_type') is not None
            and t.getDpdn('dpdn_label') is not None
        ):
            return t.setSensitive('btn_save', True)
        return t.setSensitive('btn_save', False)


    def on_buffer_changed(self, buffer, location, text, len=None):
        self.checkSave(buffer)
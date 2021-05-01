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

from gi.repository import Gtk

import deluge.component as component
from deluge.plugins.pluginbase import Gtk3PluginBase
from deluge.ui.client import client

from .common import get_resource

log = logging.getLogger(__name__)


class Gtk3UI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource('config.ui'))
        self.builder.connect_signals(Handler())

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
        #Config value is stored in a string so convert to bool
        #Capitalize first letter in case someone edited the config manually
        self.builder.get_object('chk_enable').set_active(bool(config['enabled'].capitalize()))

class Handler:
    def on_btn_list_up_clicked(self, button):
        print("Hello World")

    def on_btn_list_add_ckicked(self, button):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource('add.ui'))
        self.builder.show_all()
        Gtk.main()
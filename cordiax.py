#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import webview
import json
config = json.load(open("_config.json", "r"))
window = webview.create_window('Axia4 - EntreAulas', 'https://tech.eus/entreaulas/')
webview.start(user_agent=config["ua"])
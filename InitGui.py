# -*- coding: utf-8 -*-
# Copyright 2024 Golodnikov Sergey


import addFC_Preference as P
import FreeCAD
import FreeCADGui
import os
import re
import addFC_locator

from FreeCAD import Gui

addFCWBpath = os.path.dirname(addFC_locator.__file__)
addFCWB_icons_path = os.path.join(addFCWBpath, "Resources", "icons")

# add translations path
LanguagePath = os.path.join(addFCWBpath, "Resources", "translations")
Gui.addLanguagePath(LanguagePath)
Gui.updateLocale()


class addFC(FreeCAD.Gui.Workbench):

    MenuText = FreeCAD.Qt.translate("Workbench", 'addFC')
    ToolTip = FreeCAD.Qt.translate("Workbench", 'addFC Workbench')
    Icon = os.path.join(P.AFC_PATH_ICON, 'workbench.svg')

    import addFC

    def Initialize(self):
        self.list = [
            # core:
            'AddFCOpenRecentFile',
            'AddFCDisplay',
            'AddFCModelControl',
            'AddFCModelInfo',
            'AddFCProperties',
            'AddFCInsert',
            'AddFCAssistant',
            # utils:
            'AddFCLibrary',
            'AddFCExplode',
            'AddFCPipe',
        ]

        self.appendToolbar(FreeCAD.Qt.translate("Workbench", 'addFC'), self.list)
        self.appendMenu(FreeCAD.Qt.translate("Workbench", 'addFC'), self.list)

        global P

        FreeCAD.Gui.addPreferencePage(P.addFCPreferenceProperties, 'addFC')
        FreeCAD.Gui.addPreferencePage(P.addFCPreferenceMaterials, 'addFC')
        FreeCAD.Gui.addPreferencePage(P.addFCPreferenceSM, 'addFC')
        FreeCAD.Gui.addPreferencePage(P.addFCPreferenceOther, 'addFC')

        FreeCAD.Gui.addIconPath(P.AFC_PATH_ICON)

        font = P.pref_configuration['interface_font']
        if font[0] and font[1] != '':
            from PySide import QtGui
            QtGui.QApplication.setFont(QtGui.QFont(font[1], font[2]))

    def Activated(self): return

    def Deactivated(self): return

    def ContextMenu(self, recipient):
        self.appendContextMenu(FreeCAD.Qt.translate("Workbench", 'addFC'), self.list)

    def GetClassName(self): return 'Gui::PythonWorkbench'


FreeCAD.Gui.addWorkbench(addFC())

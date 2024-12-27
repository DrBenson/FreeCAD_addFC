# -*- coding: utf-8 -*-
# Copyright 2024 Golodnikov Sergey


from PySide import QtGui, QtCore
from zipfile import ZipFile
import addFC_Logger as Logger
import addFC_Other as Other
import addFC_Preference as P
import FreeCAD
import FreeCADGui as Gui
import json
import os
import Part
import shutil
import subprocess
import sys


VERSION = 1


DIR = os.path.join(P.AFC_PATH, 'repo', 'add', 'Library')
ZIP = os.path.join(P.AFC_PATH, 'repo', 'add', 'Library.zip')


if not os.path.exists(DIR):
    z = ZipFile(ZIP, 'r')
    z.extractall(os.path.join(P.AFC_PATH, 'repo', 'add'))
    z.close()


ui = os.path.join(os.path.dirname(__file__), 'addFC_Library.ui')
ls = os.path.join(os.path.dirname(__file__), 'addFC_Library_s.ui')


library_title, library_path, library_cache, freeze = '', '', '', False


def set_library_location(title: str, path=''):
    title = 'DIN' if title == '' else title
    match title:
        case 'DIN' | 'ISO' | 'ГОСТ': standard = True
        case _: standard = False
    global library_title
    global library_path
    global library_cache
    library_title = title
    if standard:
        library_path = os.path.join(
            P.AFC_PATH, 'repo', 'add', 'Library', title)
        library_cache = os.path.join(library_path, f'{title}_library.json')
    else:
        library_path = path if path != '' else library_list.get(title, '')
        if library_path == '':
            Logger.error(f"'{title}' unknown library...")
            return
        library_cache = os.path.join(library_path, f'{title}_library.json')
    if not os.path.exists(library_path):
        Logger.error(f"'{title}' library not found...")


configuration = P.pref_configuration

debug = configuration['library']['debug']
panel = configuration['library']['panel']

library_list = configuration['library_list']
library_recent = configuration['library']['recent']


set_library_location(library_recent)


AVAILABLE_TYPES = (
    'App::Part',
    'Part::Feature',
    'Part::FeaturePython',
    'PartDesign::Body',
)

VARIATIONS = ('Link', 'Simple', 'Copy')

LCOC_VALUES = ('Disabled', 'Enabled', 'Owned', 'Tracking')

SELECT = 'Select a library ...'

SEPARATOR = '\t'


ad = FreeCAD.activeDocument()


# ------------------------------------------------------------------------------


def library_upgrade() -> None:
    shutil.rmtree(DIR, ignore_errors=True)
    z = ZipFile(ZIP, 'r')
    z.extractall(os.path.join(P.AFC_PATH, 'repo', 'add'))
    z.close()


def logger(msg: str) -> None:
    if debug:
        Logger.log('Library ' + msg)


def grouping(expression_engine: list) -> list:
    conf = []
    if len(expression_engine) == 0:
        return conf
    for e in expression_engine:
        if len(e) < 2:
            continue
        # todo: VarSet
        if '.Enum' in e[0] and 'Spreadsheet' in e[1]:
            conf.append(str(e[0][1:].replace('.Enum', '')))
    return conf


def dissection(dp: str, close: bool) -> dict:
    structure = {}
    doc = FreeCAD.openDocument(dp, True)
    FreeCAD.setActiveDocument(ad.Name)
    for t in AVAILABLE_TYPES:
        for o in doc.findObjects(t):
            if 'Add_Name' not in o.PropertiesList:
                continue
            group = {}
            for g in grouping(o.ExpressionEngine):
                if g != '' and g in o.PropertiesList:
                    group[g] = o.getEnumerationsOfProperty(g)
            structure[o.Label] = group
    if close:
        FreeCAD.closeDocument(doc.Name)
    return structure


class widget():
    library, info, target = {}, {}, []
    cache_search, cache_conf, cache_objects = {}, {}, []

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(ui)
        if not panel:
            self.form.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            self.form.show()
            self.form.search.setFocus()

        self.form.choice.addItems(library_list.keys())
        self.form.choice.addItem(SELECT)
        self.form.choice.setCurrentText(library_title)

        self.form.variation.addItems(VARIATIONS)
        self.form.lcoc.addItems(LCOC_VALUES)

        def variance(var) -> None:
            self.form.lcoc.setEnabled(True if var == 'Link' else False)

        self.form.variation.setCurrentText(
            configuration['library']['variation'])
        self.form.lcoc.setCurrentText(
            configuration['library']['lcoc'])

        variance(configuration['library']['variation'])

        self.form.refreshLibrary.clicked.connect(self.refresh)
        self.refresh()

        keys = list(self.library.keys())
        if len(keys) == 0:
            keys.append('The library is empty')

        # files:

        def fileLibrary(catalog) -> None:
            self.form.fileLibrary.clear()
            self.form.group.clear()
            self.form.configuration.clear()
            self.form.group.setEnabled(False)
            self.form.configuration.setEnabled(False)
            if catalog in self.library:
                self.form.fileLibrary.addItems(self.library[catalog].keys())

        self.form.catalogLibrary.currentTextChanged.connect(fileLibrary)
        fileLibrary(keys[0])

        # objects:

        model = QtGui.QStandardItemModel()

        def objects() -> None:
            self.target.clear()
            self.form.add.setEnabled(False)

            self.form.group.clear()
            self.form.configuration.clear()
            self.form.group.setEnabled(False)
            self.form.configuration.setEnabled(False)

            model.clear()
            self.form.objects.setModel(model)

            catalog = self.form.catalogLibrary.currentText()
            file = self.form.fileLibrary.currentText()

            if catalog not in self.library:
                return
            if file not in self.library[catalog]:
                return

            if 'objects' in self.library[catalog][file]:
                for obj in self.library[catalog][file]['objects']:
                    model.appendRow(QtGui.QStandardItem(obj))

        self.form.fileLibrary.currentTextChanged.connect(objects)
        objects()

        # configurations:

        def conf(item) -> None:
            self.target.clear()
            self.form.add.setEnabled(False)

            self.form.group.clear()
            self.form.configuration.clear()
            self.form.group.setEnabled(False)
            self.form.configuration.setEnabled(False)

            conf_search = self.form.searchInConf.isChecked()

            object = model.index(item.row(), item.column()).data()

            if not conf_search:
                conf = ''
            else:
                sp = object.split(SEPARATOR)
                if len(sp) == 2:
                    conf, object = sp[0], sp[1]
                else:
                    pass  # todo: error?

            for i in self.cache_objects:
                if object == i[0]:
                    catalog, file = i[2], i[1]

            self.cache_conf = self.library[catalog][file]['objects'][object]
            self.target = [catalog, file, object]

            self.form.add.setEnabled(True)

            groups = list(self.cache_conf.keys())
            if len(groups) == 0:
                return
            obj_configurations = self.cache_conf[groups[0]]

            self.form.group.addItems(groups)

            if len(groups) > 1:
                self.form.group.setEnabled(True)
            if len(obj_configurations) > 0:
                self.form.configuration.setEnabled(True)
            if conf != '':
                self.form.configuration.setEnabled(False)
                self.form.configuration.setCurrentText(conf)

        self.form.objects.clicked.connect(conf)

        # grouping:

        def grouping(group) -> None:
            self.form.configuration.clear()
            self.form.configuration.setEnabled(False)
            if group in self.cache_conf:
                self.form.configuration.addItems(self.cache_conf[group])
                self.form.configuration.setEnabled(True)

        self.form.group.currentTextChanged.connect(grouping)

        # object search:

        def search(s) -> None:
            # todo: dictionary search faster...
            model.clear()
            if s == '':
                objects()
            else:
                if not self.form.searchInConf.isChecked():
                    # standard search:
                    for i in self.cache_objects:
                        if s.lower() in i[0].lower():
                            model.appendRow(QtGui.QStandardItem(i[0]))
                else:
                    # search in configurations:
                    for i in self.cache_search:
                        if s.lower() in i.lower():
                            for j in self.cache_search[i]:
                                model.appendRow(QtGui.QStandardItem(
                                    i + SEPARATOR + j[2]))

        self.form.search.textEdited.connect(search)

        # variations:

        self.form.variation.currentTextChanged.connect(variance)

        # change library root directory:

        def choice_update():
            global freeze
            freeze = True
            self.form.choice.clear()
            self.form.choice.addItems(library_list.keys())
            self.form.choice.addItem(SELECT)
            self.form.choice.setCurrentText(library_title)
            freeze = False

        def change(target) -> None:
            global freeze
            if freeze or target == library_title:
                return
            if target == SELECT:
                d = os.path.normcase(QtGui.QFileDialog.getExistingDirectory())
                if d == '':
                    return
                path = d
            else:
                path = ''

            self.clear()

            if path == '':
                # library from the list:
                set_library_location(target)
            else:
                # new library:
                title = os.path.basename(path)
                set_library_location(title, path)
                global library_list
                library_list[title] = path

            # saving the configuration:
            global configuration
            configuration['library']['recent'] = library_title
            configuration['library_list'] = library_list
            P.save_pref(P.PATH_CONFIGURATION, configuration)

            self.refresh()
            choice_update()

        self.form.choice.currentTextChanged.connect(change)

        # open library root directory:

        def open_library() -> None:
            match sys.platform:
                case 'win32': subprocess.run(['explorer', library_path])
                case 'darwin': subprocess.run(['open', library_path])
                case _: subprocess.run(['xdg-open', library_path])

        self.form.openLibrary.clicked.connect(open_library)

        # add or replace object:

        def integration(replace: bool) -> None:
            catalog, file, label = self.target
            file += '.FCStd'

            bn = os.path.basename(library_path)
            if catalog == bn:
                dp = os.path.join(library_path, file)
            else:
                dp = os.path.join(library_path, catalog, file)

            placement, root = extra(replace)

            add_object(
                dp,
                label,
                self.form.group.currentText(),
                self.form.configuration.currentText(),
                self.form.variation.currentText(),
                self.form.lcoc.currentText(),
                placement,
                root,
            )

        def add() -> None: integration(False)

        def replace() -> None:
            # the button is always active...
            if len(FreeCAD.Gui.Selection.getSelection()) > 0:
                try:
                    integration(True)
                except BaseException:
                    pass

        self.form.add.clicked.connect(add)
        self.form.replace.clicked.connect(replace)

        # preferences:

        def preferences() -> None:
            pref = {
                'debug': configuration['library']['debug'],
                'panel': configuration['library']['panel'],
            }

            u = FreeCAD.Gui.PySideUic.loadUi(ls)

            u.panel.setChecked(pref['panel'])
            u.debug.setChecked(pref['debug'])

            # information about the library:

            u.name.setText(library_title)
            u.catalogs.setText(f"Catalogs - {self.info['catalogs']}")
            u.files.setText(f"Files - {self.info['files']}")
            u.objects.setText(f"Objects - {self.info['objects']}")

            # standard library:
            update = False
            try:
                f = open(os.path.join(DIR, 'Version'), 'r')
                s = f.readline().strip('\n')
                f.close()
                v = int(s)
                if v < VERSION:
                    update = True
                elif v > VERSION:
                    v = 'error'
                    update = True
            except BaseException:
                v = 'error'
                update = True

            u.workbench.setText(f'Workbench version - {VERSION}')
            u.local.setText(f'Local version - {v}')

            if v == 'error' or update:
                u.local.setStyleSheet('color: #960000')

            u.refresh.setEnabled(update)

            def library_upgrade_wrapper() -> None:
                library_upgrade
                u.local.setText(f'Local version - {VERSION}')
                u.local.setStyleSheet('')
                u.restart.setText(
                    'Update complete, library needs to be restarted')
                u.refresh.setEnabled(False)

            u.refresh.clicked.connect(library_upgrade_wrapper)

            u.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            u.show()

            def apply() -> None:
                pref['debug'] = u.debug.isChecked()
                pref['panel'] = u.panel.isChecked()
                global configuration
                configuration['library'].update(pref)
                P.save_pref(P.PATH_CONFIGURATION, configuration)
                u.close()

            u.apply.clicked.connect(apply)

        self.form.preferences.clicked.connect(preferences)

    # save and restore library:

    def storage(self) -> None:
        if len(self.library) != 0:
            file = open(library_cache, 'w+', encoding='utf-8')
            json.dump(self.library, file, ensure_ascii=False)
            file.close()

    def recovery(self):
        if os.path.exists(library_cache):
            try:
                file = open(library_cache, 'r', encoding='utf-8')
                self.library = json.load(file)
                file.close()
            except BaseException as e:
                Logger.error(str(e))

    # library update:

    def refresh(self):
        self.clear()
        self.recovery()

        # update:

        ld = tuple(FreeCAD.listDocuments().keys())

        fresh = {'catalogs': [], 'files': []}

        for address, _, files in os.walk(library_path):
            catalog = os.path.basename(address)
            fresh['catalogs'].append(catalog)

            if catalog not in self.library:
                new_catalog = True
                self.library[catalog] = {}
            else:
                new_catalog = False

            for f in files:
                fn, fe = os.path.splitext(f)
                if fe != '.FCStd':
                    continue

                fresh['files'].append(fn)

                dp = os.path.join(address, f)
                t = os.path.getmtime(dp)

                if fn in self.library[catalog]:
                    if t == self.library[catalog][fn]['timestamp']:
                        continue
                    else:
                        _ = self.library[catalog].pop(fn, None)
                        logger('[file] update: ' + fn)
                else:
                    logger('[file] add: ' + fn)

                objects = dissection(dp, False if fn in ld else True)

                self.library[catalog][fn] = {
                    'timestamp': t,
                    'objects': objects
                }

            if len(self.library[catalog]) == 0:
                _ = self.library.pop(catalog, None)
                fresh['catalogs'].remove(catalog)
            elif new_catalog:
                logger('[catalog] add: ' + catalog)

        # check:

        bn = os.path.basename(library_path)
        for catalog in list(self.library.keys()):
            if bn != catalog:
                if catalog not in fresh['catalogs']:
                    _ = self.library.pop(catalog, None)
                    logger('[catalog] deleted: ' + catalog)
            for f in list(self.library[catalog].keys()):
                if f not in fresh['files']:
                    _ = self.library[catalog].pop(f, None)
                    logger('[file] deleted: ' + f)

        # updating cache and structure information:

        files, objects = 0, 0
        for catalog in self.library:
            for file in self.library[catalog]:
                files += 1
                if 'objects' in self.library[catalog][file]:
                    for obj in self.library[catalog][file]['objects']:
                        objects += 1
                        self.cache_objects.append((obj, file, catalog))
                        # to search in configurations:
                        value = self.library[catalog][file]['objects'][obj]
                        if 'Conf' in value:
                            for conf in value['Conf']:
                                i = [catalog, file, obj]
                                if conf in self.cache_search:
                                    self.cache_search[conf].append(i)
                                else:
                                    self.cache_search[conf] = [i,]

        self.info['catalogs'] = len(list(self.library.keys()))
        self.info['files'] = files
        self.info['objects'] = objects

        # init and save:

        keys = list(self.library.keys())
        if len(keys) == 0:
            keys.append('The library is empty')
            self.form.catalogLibrary.setEnabled(False)
            self.form.fileLibrary.setEnabled(False)
        else:
            self.form.catalogLibrary.setEnabled(True)
            self.form.fileLibrary.setEnabled(True)
        self.form.catalogLibrary.addItems(keys)
        self.form.catalogLibrary.setCurrentText(keys[0])

        self.storage()

    # other:

    def clear(self) -> None:
        self.library.clear()
        self.cache_search.clear()
        self.cache_conf.clear()
        self.cache_objects.clear()
        self.form.catalogLibrary.clear()
        self.form.fileLibrary.clear()
        self.form.group.clear()
        self.form.configuration.clear()

    def accept(self):
        global configuration
        configuration['library'].update({
            'lcoc': self.form.lcoc.currentText(),
            'recent': library_title,
            'sic': self.form.searchInConf.isChecked(),
            'variation': self.form.variation.currentText(),
        })
        P.save_pref(P.PATH_CONFIGURATION, configuration)
        Gui.Control.closeDialog()


# ------------------------------------------------------------------------------


def add_object(dp: str,
               label: str,
               group: str,
               conf: str,
               var: str,
               lcoc: str,
               placement: FreeCAD.Placement,
               root: str) -> None:

    ld = FreeCAD.listDocuments()

    doc = FreeCAD.openDocument(dp, True)
    FreeCAD.setActiveDocument(ad.Name)

    opened = True if doc.Name in ld else False

    try:
        src = doc.getObjectsByLabel(label)[0]
    except BaseException as e:
        Logger.error(str(e))

    if var != 'Link':
        if conf != '' and group != '' and group in src.PropertiesList:
            setattr(src, group, conf)  # apply configuration
            doc.recompute()
    else:
        if not ad.isSaved():
            Other.error('Owner document not saved', 'Create link failed')
            return

    match var:
        case 'Link':
            dst = ad.addObject('App::Link', 'Link')
            dst.setLink(src)
            dst.LinkCopyOnChange = lcoc
            if conf != '' and group != '' and group in src.PropertiesList:
                setattr(dst, group, conf)  # apply configuration
            ad.recompute()
            dst.Placement = placement
            rename(src, dst)

        case 'Simple':
            shape = Part.getShape(src, '', needSubElement=False, refine=False)
            dst = ad.addObject('Part::Feature', 'Feature')
            dst.Shape = shape
            dst.Placement = placement
            rename(src, dst)
            try:
                dst.ViewObject.ShapeColor = src.ViewObject.ShapeColor
                dst.ViewObject.LineColor = src.ViewObject.LineColor
                dst.ViewObject.PointColor = src.ViewObject.PointColor
            except BaseException:
                pass
            for p in src.PropertiesList:
                if 'Add_' in p:
                    dst.addProperty(src.getTypeIdOfProperty(p), p, 'Add')
                    dst.restorePropertyContent(p, src.dumpPropertyContent(p))
            if not opened:
                FreeCAD.closeDocument(doc.Name)

        case 'Copy':
            dst = ad.copyObject(src, True, True)
            dst.Placement = placement
            rename(src, dst)
            if not opened:
                FreeCAD.closeDocument(doc.Name)

    if root != '':
        ad.getObject(root).addObject(dst)

    ad.recompute()

    # required for correct recalculation of configuration tables:
    if P.FC_VERSION[1] == '21':
        try:
            Other.recompute_configuration_tables()
        except BaseException:
            pass


# ------------------------------------------------------------------------------


def rename(src, dst) -> None:
    if 'Add_Name' in src.PropertiesList:
        dst.Label = src.getPropertyByName('Add_Name') + ' 001'
    else:
        dst.Label = src.Label + ' 001'


def extra(replace: bool) -> tuple[FreeCAD.Placement, str]:
    placement, root = FreeCAD.Placement(), ''

    objects = ad.findObjects('App::Part')
    if len(objects) > 0:
        obj = objects[0]
        match obj.TypeId:
            case 'App::Part' | 'Assembly::AssemblyObject': root = obj.Name

    vector, obj = FreeCAD.Vector(), None

    try:
        selection = FreeCAD.Gui.Selection.getSelectionEx('', 0)
        if len(selection) == 0:
            return placement, root
        selection = selection[0]
        if selection.HasSubObjects:
            vector += selection.SubObjects[0].BoundBox.Center
        placement.Base += vector

        try:
            sen = selection.SubElementNames[0]
            sol = selection.Object.getSubObjectList(sen)
            zero = sol[0]
            if zero.TypeId == 'App::Part':
                root = zero.Name
            if len(sol) == 1:
                obj = zero
            else:
                obj = sol[-1]
                match obj.TypeId:
                    case 'App::Link' | 'Part::Feature':
                        pass
                    case _:
                        obj = sol[-2]
        except BaseException as e:
            Logger.warning(str(e))

    except BaseException as e:
        Logger.warning(str(e))
        placement.Base += selection.PickedPoints[0]

    if (replace and obj is not None):
        placement = obj.Placement
        match obj.TypeId:
            case 'App::Link':
                lo = obj.getLinkedObject()
                if 'Add_Name' in lo.PropertiesList:
                    ad.removeObject(obj.Name)
                else:
                    Logger.warning('unsupported object to replace...')
            case 'Part::Feature':
                if 'Add_Name' in obj.PropertiesList:
                    ad.removeObject(obj.Name)
                else:
                    Logger.warning('unsupported object to replace...')
            case _:
                Logger.warning('unsupported object type to replace...')
                root = ''
        ad.recompute()

    return placement, root


# ------------------------------------------------------------------------------


if panel:
    w = widget()
    Gui.Control.showDialog(w)
    w.form.search.setFocus()
else:
    widget()
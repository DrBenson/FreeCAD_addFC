# -*- coding: utf-8 -*-
# Copyright 2025 Golodnikov Sergey


import os
import FreeCAD

configuration = {
    'interface_font': [False, 'Blender Mono I18n', 10],
    'working_directory': '',
    'default_material': 'Galvanized',
    # unfold:
    'unfold_dxf': True,
    'unfold_svg': False,
    'unfold_stp': False,
    'unfold_centering': False,
    'unfold_along_x': False,
    'unfold_file_name': 'Index',
    'unfold_file_signature': 'None',
    'unfold_prefix': 'Unfold',
    # bill of materials:
    'bom_export_type': 'Spreadsheet',
    'bom_export_alias': ['csv', 'spreadsheet'],
    'bom_export_merger': 'Type',
    'bom_export_sort': 'Index',
    'bom_export_skip': [],
    # sheet metal part:
    'smp_color': tuple(int('b4c0c8'[i:i + 2], 16) for i in (0, 2, 4)),
    # USDD:
    'std_tpl_drawing': 'Portrait_A4.svg',
    'std_tpl_text': 'Portrait_A4_T_1.svg',
    'std_tpl_stamp': {
        'Designation': 'XXXX.XXXXXX.XXX',
        'Author': '',
        'Inspector': '',
        'Control 1': '',
        'Control 2': '',
        'Approver': '',
        'Material 1': '',
        'Material 2': '',
        'Company 1': '',
        'Company 2': '',
        'Company 3': '',
        'Title 1': '',
        'Title 2': '',
        'Title 3': '',
        'Weight': '',
        'Scale': '1:1',
        'Letter 1': '',
        'Letter 2': '',
        'Letter 3': '',
    },
    # library:
    'library': {
        'debug': False,
        'lcoc': 'Enabled',
        'panel': True,
        'recent': 'DIN',
        'sic': False,
        'variation': 'Simple',
    },
    'library_list': {
        # standard:
        'DIN': None,
        'ISO': None,
        'ГОСТ': None,
    },
}


explosion = {
    'export_size': '1080p (FHD)',
    'export_width': 1920,
    'export_height': 1080,
    'export_background': 'Current',
    'export_method': 'Framebuffer',
    'export_ccs': False,
    'export_image_format': 'PNG',
    'export_framerate': 60,
    'export_dir': os.path.expanduser(FreeCAD.Qt.translate("Form",'~/Desktop')),
}


# materials = title: [category, density, unit, price per unit]

materials = {
    '-': None,
    # standard:
    'Galvanized': ['Sheet metal', 7874, 'm^2', 4],
    'Stainless': ['Sheet metal', 7900, 'm^2', 4.2],
    # general:
    'Aluminum': ['General', 2780, 'kg', 0],
    'Brass': ['General', 8600, 'kg', 0],
    'Cast iron': ['General', 7874, 'kg', 4],
    'Ceramic': ['General', 2300, 'kg', 0],
    'Concrete': ['General', 2410, 'm^3', 0],
    'Copper': ['General', 8900, 'kg', 0],
    'Glass': ['General', 2530, 'kg', 0],
    'Mineral wool': ['General', 100, 'm^2', 0],
    'Rubber': ['General', 1000, 'kg', 0],
    'Steel': ['General', 7850, 'kg', 4],
    # aisi:
    'AISI 201': ['Sheet metal', 7860, 'm^2', 0],
    'AISI 304': ['Sheet metal', 7950, 'm^2', 0],
    'AISI 316': ['Sheet metal', 7970, 'm^2', 0],
    'AISI 321': ['Sheet metal', 8020, 'm^2', 0],
    'AISI 430': ['Sheet metal', 7720, 'm^2', 0],
    # plastic:
    'ABS': ['Plastic', 1040, 'kg', 11.5],
    'PC/Fiber': ['Plastic', 1.55, 'kg', 19],
    'PET/G': ['Plastic', 1340, 'kg', 30],
    'PLA': ['Plastic', 1240, 'kg', 0],
    'PP': ['Plastic', 905, 'kg', 8.7],
    'PVC': ['Plastic', 1330, 'kg', 6.6],
    # rubber:
    'EPDM': ['Rubber', 155, 'kg', 0],
    'Natural rubber': ['Rubber', 920, 'kg', 0],
    'Neoprene': ['Rubber', 1230, 'kg', 0],
    # wood:
    'Wood, low density': ['Wood', 500, 'm^3', 0],
    'Wood, medium density': ['Wood', 700, 'm^3', 0],
    'Wood, high density': ['Wood', 900, 'm^3', 0],
}


# properties = title: [type, addition, [enumeration], alias]

properties_core = {
    # required:
    'Name': ['String', True, [], FreeCAD.Qt.translate("Form",'Name')],
    # core:
    'Code': ['String', False, [], FreeCAD.Qt.translate("Form",'Code')],
    'Index': ['String', True, [], FreeCAD.Qt.translate("Form",'Index')],
    'Material': ['Enumeration', False, ['-', 'Galvanized', 'Stainless', ], FreeCAD.Qt.translate("Form",'Material')],
    'MetalThickness': ['Float', False, [], FreeCAD.Qt.translate("Form",'Metal Thickness')],
    'Node': ['String', False, [], FreeCAD.Qt.translate("Form",'Node')],
    'Price': ['Float', True, [], FreeCAD.Qt.translate("Form",'Price')],
    'Quantity': ['Float', True, [], FreeCAD.Qt.translate("Form",'Quantity')],
    'Unfold': ['Bool', False, [], FreeCAD.Qt.translate("Form",'Unfold')],
    'Unit': ['Enumeration', False, ['-', 'm', 'kg', 'm^2', 'm^3'], FreeCAD.Qt.translate("Form",'Unit')],
    'Weight': ['Float', True, [], FreeCAD.Qt.translate("Form",'Weight')],
}

properties_add = {
    # additional:
    'Format': ['Enumeration', False, ['-', 'A0', 'A1', 'A2', 'A3', 'A4'], FreeCAD.Qt.translate("Form",'Format')],
    'Id': ['String', False, [], FreeCAD.Qt.translate("Form",'Id')],
    'Note': ['String', False, [], FreeCAD.Qt.translate("Form",'Note')],
    'Type': ['Enumeration', False, [
        '-',
        FreeCAD.Qt.translate("Form",'Part'),
        FreeCAD.Qt.translate("Form",'Sheet metal part'),
        FreeCAD.Qt.translate("Form",'Fastener'),
        FreeCAD.Qt.translate("Section",'Material'),
    ], FreeCAD.Qt.translate("Form",'Type')],
    # разделы спецификации ЕСКД:
    'Section': ['Enumeration', False, [
        '-',
        FreeCAD.Qt.translate("Form",'Documentation'),
        FreeCAD.Qt.translate("Form",'Complexes'),
        FreeCAD.Qt.translate("Form",'Assembly units'),
        FreeCAD.Qt.translate("Form",'Parts'),
        FreeCAD.Qt.translate("Form",'Standard products'),
        FreeCAD.Qt.translate("Form",'Other products'),
        FreeCAD.Qt.translate("Section",'Materials'),
        FreeCAD.Qt.translate("Form",'Kits'),
    ], FreeCAD.Qt.translate("Form",'Section')],
}


# steel = title: {thickness: [radius, k-factor]}

steel = {
    'Galvanized': {
        '0.35': [1.0, 0.475],
        '0.4': [1.0, 0.472],
        '0.45': [1.0, 0.469],
        '0.5': [1.0, 0.466],
        '0.55': [1.0, 0.464],
        '0.6': [1.0, 0.461],
        '0.65': [1.0, 0.458],
        '0.7': [1.3, 0.464],
        '0.75': [1.3, 0.462],
        '0.8': [1.3, 0.460],
        '0.9': [1.3, 0.456],
        '1.0': [1.3, 0.453],
        '1.2': [1.7, 0.456],
        '1.4': [1.7, 0.450],
        '1.5': [1.7, 0.448],
        '1.8': [1.7, 0.440],
        '2.0': [2.7, 0.454],
        '2.5': [2.7, 0.446],
        '3.0': [3.3, 0.446],
        '3.5': [3.3, 0.440],
    },
    'Stainless': {
        '0.4': [1.0, 0.472],
        '0.5': [1.0, 0.466],
        '0.6': [1.0, 0.461],
        '0.7': [1.3, 0.464],
        '0.8': [1.3, 0.460],
        '0.9': [1.3, 0.456],
        '1.0': [1.3, 0.453],
        '1.2': [1.7, 0.456],
        '1.5': [1.7, 0.448],
        '2.0': [2.7, 0.454],
        '2.5': [2.7, 0.446],
        '3.0': [3.3, 0.446],
        '4.0': [5.3, 0.453],
        '5.0': [6.7, 0.454],
        '6.0': [8.3, 0.455],
        '8.0': [10.5, 0.453],
        '10.0': [13.3, 0.454],
        '12.0': [16.7, 0.455],
    },
}

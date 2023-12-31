from PySide6 import QtCore, QtGui, QtWidgets

import stfed.factories.ani
import stfed.factories.tlb
import stfed.factories.pal
import stfed.model
from stfed.model import ResourceType
import stfed.consts
from stfed.view.autogenerated.Ui_TlbResourcePreview import Ui_TlbResourcePreview
from stfed.repos.resources import resources_repo_instance as resources_repo
from stfed.repos.user_preferences import repo as user_preferences_repo
from stfed.repos.preview_images import preview_images_repo_instance as preview_images_repo
from stfed.view.ImageDelegate import ImageDelegate
import stfed.view.ThreadWrapper

PREVIEW_DEFAULT_SIZE = 100, 100
_TERRAIN_TABLE_PIXMAP_COLUMN = 1
_TILES_TABLE_PIXMAP_COLUMN = 2

class TlbResourcePreview(QtWidgets.QWidget, Ui_TlbResourcePreview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__model = None
        self.__terrain_pixmaps = []
        self.__tile_pixmaps = []
        self.__labels = []
        self.__dialog = None
        self.__subscriptions = []
        
        self.__subscriptions.append(
            user_preferences_repo.values().subscribe(
                lambda up: self.__on_double_width_preview_pref_changed(up.double_width_image_preview)))


        terrain_table_headers = [
            "Id",
            "Portrait",
            "Name",
            "MOV",
            "ATK",
            "RAN",
            "DEF",
            "Damage",
            "Burnable",
            "Color"
        ]
        self.terrain_table.setColumnCount(len(terrain_table_headers))
        self.terrain_table.setHorizontalHeaderLabels(terrain_table_headers)
        self.terrain_table.setItemDelegate(ImageDelegate(None))
        self.terrain_table.setVisible(False)
        tile_table_headers = [
            "Id",
            "Terrain",
            "Bitmap",
            "Animation",
            "Ani. delay",
            "Swap tile"
        ]
        self.tiles_table.setColumnCount(len(tile_table_headers))
        self.tiles_table.setHorizontalHeaderLabels(tile_table_headers)
        self.tiles_table.setItemDelegate(ImageDelegate(None))
        
        self.terrain_toggle.clicked.connect(self.__terrain_toggle_clicked)
        self.tiles_toggle.clicked.connect(self.__tiles_toggle_clicked)


    def set_model(self, resource: stfed.model.Resource):
        self.__labels.clear()
                    
        palettes = [
            r for r in resources_repo.all_resources(look_in_default_lookup_paths=True)
            if r.resource_type == ResourceType.PAL.value
        ]
        pal_res = [p for p in palettes if p.resource_name == resource.resource_name]
        error = None
        if len(pal_res) == 0:
            pal_res = [p for p in palettes if p.resource_name == 9100]
            error = f"Could not find the corresponding palette {resource.resource_name}.PAL, falling back to 9100.PAL instead."
        if len(pal_res) == 0:
            pal_res = None
            palette = [(i, i, i) for i in range(256)]
            error =f"Could not find the corresponding palette {resource.resource_name}.PAL or 9100.PAL, falling back to monochrome instead."
        if error is not None:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setText(error)
            msgBox.setWindowTitle("Error")
            msgBox.exec()
        if pal_res != None:
            palette = stfed.factories.pal.parse(pal_res[0].data()).data

        model = stfed.factories.tlb.parse_tile_library(resource.data())
        self.__model = model
        self.__terrain_pixmaps = [None for _ in model.terrains]
        self.__tile_pixmaps = [None for _ in model.tiles]
        self.tiles_table.setRowCount(0)
        self.terrain_table.setRowCount(0)
        self.tiles_table.setRowCount(len(model.tiles))
        self.terrain_table.setRowCount(len(model.terrains))
        adj = 2 if user_preferences_repo.get().double_width_image_preview else 1
        for i, terrain in enumerate(model.terrains):
            def format_modifier(value: int) -> str:
                if value == 0:
                    return ''
                sign = '+' if value > 0 else ''
                return sign + str(value)
            
            self.terrain_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i)))
            self.terrain_table.setItem(i, 2, QtWidgets.QTableWidgetItem(terrain.name))
            self.terrain_table.setItem(i, 3, QtWidgets.QTableWidgetItem(format_modifier(-terrain.move_rate)))
            self.terrain_table.setItem(i, 4, QtWidgets.QTableWidgetItem(format_modifier(terrain.attack_mod)))
            self.terrain_table.setItem(i, 5, QtWidgets.QTableWidgetItem(format_modifier(terrain.attack_range_mod)))
            self.terrain_table.setItem(i, 6, QtWidgets.QTableWidgetItem(format_modifier(terrain.defense_mod)))
            self.terrain_table.setItem(i, 7, QtWidgets.QTableWidgetItem(str(terrain.damage_val) if terrain.damage_val > 0 else ''))
            self.terrain_table.setItem(i, 8, QtWidgets.QTableWidgetItem('Y' if terrain.burnable > 0 else ''))
            c = palette[terrain.color]
            it = QtWidgets.QTableWidgetItem(str(terrain.color))
            it.setBackground(QtGui.QColor(*c))
            it.setForeground(QtGui.QColor(255 - c[0], 255 - c[1], 255 - c[2]))
            self.terrain_table.setItem(i, 9, it)

        self.terrain_table.setColumnWidth(1, PREVIEW_DEFAULT_SIZE[0])
        self.terrain_table.setColumnWidth(2, PREVIEW_DEFAULT_SIZE[0])
        for r in range(len(model.terrains)):
            self.terrain_table.setRowHeight(r, PREVIEW_DEFAULT_SIZE[1])
        self.terrain_table.setFixedHeight((len(model.terrains) + 1) * PREVIEW_DEFAULT_SIZE[1])
        #self.terrain_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        for i, tile in enumerate(model.tiles):
            self.tiles_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i)))
            self.tiles_table.setItem(i, 1, QtWidgets.QTableWidgetItem(tile.terrain_type.name))
            self.tiles_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(tile.ani_res) if tile.ani_res > 0 else ""))
            self.tiles_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(tile.ani_delay)  if tile.ani_delay > 0 else ""))
            self.tiles_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(tile.swap_tile) if tile.swap_tile > 0 else ""))

        self.tiles_table.setColumnWidth(1, PREVIEW_DEFAULT_SIZE[0])
        self.tiles_table.setColumnWidth(2, PREVIEW_DEFAULT_SIZE[0])
        for r in range(len(model.tiles)):
            self.tiles_table.setRowHeight(r, PREVIEW_DEFAULT_SIZE[1])
        self.tiles_table.setFixedHeight((len(model.tiles) + 1) * PREVIEW_DEFAULT_SIZE[1])
        
        def generate_images(progress_signal):
            rns = [x for x in range(2640, 2800)] + [2592]
            for i, rn in enumerate(rns):
                key = ("portraits", rn, ResourceType.ANI)
                maybe_bitmap = preview_images_repo.get(*key)
                if maybe_bitmap is None:
                    portrait_res =resources_repo.get(rn, ResourceType.ANI)
                    if portrait_res is None:
                        continue
                    progress_signal.emit(float(i)/len(rns) * 0.5, f"Generating terrain portrait ({i}/{len(rns)})...")
                    portrait_ani = stfed.factories.ani.parse(portrait_res)
                    maybe_bitmap = stfed.factories.ani.export_image(portrait_ani.cels[0], stfed.model.Palette(palette))
                    preview_images_repo.put(*key, maybe_bitmap)

            for i, tile in enumerate(model.tiles):
                if preview_images_repo.get(resource.source_file, resource.resource_name, ResourceType.TLB, i, str(stfed.model.Side.SIDE1.name)) is not None:
                    continue
                progress_signal.emit(0.5 + float(i)/len(model.tiles) * 0.5, f"Generating tile ({i}/{len(model.tiles)})...")
                maybe_bitmap = stfed.factories.tlb.export_single_tile_image(tile, stfed.model.Palette(palette))
                preview_images_repo.put(resource.source_file, resource.resource_name, ResourceType.TLB, maybe_bitmap, i, str(stfed.model.Side.SIDE1.name))
            progress_signal.emit(1, "Done")

        all_portaits_generated = True
        for i, terrain in enumerate(self.__model.terrains):
            if terrain.portrait_num == 0:
                continue
            portrait_pixmap = None
            key = ("portraits", terrain.portrait_num, ResourceType.ANI)
            maybe_bitmap = preview_images_repo.get(*key)
            if maybe_bitmap is None:
                all_portaits_generated = False
                continue
            portrait_pixmap = QtGui.QPixmap()
            portrait_pixmap.loadFromData(maybe_bitmap, 'PNG')
            self.__terrain_pixmaps[i] = portrait_pixmap
            portrait_pixmap = portrait_pixmap.scaled(portrait_pixmap.width() * adj, portrait_pixmap.height())
            self.terrain_table.setItem(i, _TERRAIN_TABLE_PIXMAP_COLUMN, QtWidgets.QTableWidgetItem(portrait_pixmap, ""))
        all_tiles_generated = True
        for i, _ in enumerate(self.__model.tiles):
            maybe_bitmap = preview_images_repo.get(resource.source_file, resource.resource_name, ResourceType.TLB, i, stfed.model.Side.SIDE1.name)
            if maybe_bitmap is None:
                all_tiles_generated = False
                continue
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(maybe_bitmap, 'PNG')
            self.__tile_pixmaps[i] = pixmap  
            pixmap = pixmap.scaled(pixmap.width() * adj, pixmap.height())
            self.tiles_table.setItem(i, _TILES_TABLE_PIXMAP_COLUMN, QtWidgets.QTableWidgetItem(pixmap, ""))

        def on_images_generated():
            self.__dialog.close()
            self.__dialog = None
            for i, terrain in enumerate(self.__model.terrains):
                portrait_pixmap = None
                key = ("portraits", terrain.portrait_num, ResourceType.ANI)
                maybe_bitmap = preview_images_repo.get(*key)
                if maybe_bitmap is None:
                    continue
                portrait_pixmap = QtGui.QPixmap()
                portrait_pixmap.loadFromData(maybe_bitmap, 'PNG')
                self.__terrain_pixmaps[i] = portrait_pixmap
                portrait_pixmap = portrait_pixmap.scaled(portrait_pixmap.width() * adj, portrait_pixmap.height())
                self.terrain_table.setItem(i, _TERRAIN_TABLE_PIXMAP_COLUMN, QtWidgets.QTableWidgetItem(portrait_pixmap, ""))
            for i, _ in enumerate(self.__model.tiles):
                maybe_bitmap = preview_images_repo.get(resource.source_file, resource.resource_name, ResourceType.TLB, i, stfed.model.Side.SIDE1.name)
                if maybe_bitmap is None:
                    continue
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(maybe_bitmap, 'PNG')
                self.__tile_pixmaps[i] = pixmap         
                pixmap = pixmap.scaled(pixmap.width() * adj, pixmap.height())
                self.tiles_table.setItem(i, _TILES_TABLE_PIXMAP_COLUMN, QtWidgets.QTableWidgetItem(pixmap, ""))

        if not all_portaits_generated or not all_tiles_generated:
            self.__dialog = stfed.view.BackgroundOperationWindow.BackgroundOperationWindow()
            self.__dialog.show()
            self.background_operation = stfed.view.ThreadWrapper.ThreadWrapper(generate_images)
            self.background_operation.finished.connect(on_images_generated)
            self.background_operation.on_progress.connect(self.__dialog.set_progress)
            self.background_operation.start()


    def __on_double_width_preview_pref_changed(self, new_value: bool):
        for i in range(len(self.__terrain_pixmaps)):
            pixmap = self.__terrain_pixmaps[i]
            if pixmap is None:
                continue
            if new_value:
                pixmap = pixmap.scaled(pixmap.width() * 2, pixmap.height())
            self.terrain_table.setItem(i, _TERRAIN_TABLE_PIXMAP_COLUMN, QtWidgets.QTableWidgetItem(pixmap, ""))
            
        for i in range(len(self.__tile_pixmaps)):
            pixmap = self.__tile_pixmaps[i]
            if pixmap is None:
                continue
            if new_value:
                pixmap = pixmap.scaled(pixmap.width() * 2, pixmap.height())
            self.tiles_table.setItem(i, _TILES_TABLE_PIXMAP_COLUMN, QtWidgets.QTableWidgetItem(pixmap, ""))


    def __terrain_toggle_clicked(self):
        self.__toggle(self.terrain_toggle, self.terrain_table)

    def __tiles_toggle_clicked(self):
        self.__toggle(self.tiles_toggle, self.tiles_table)

    def __toggle(self, header: QtWidgets.QPushButton, contents: QtWidgets.QWidget):
        is_visible = contents.isVisible()
        new_icon = '-' if is_visible else '+'
        header.setText(new_icon + header.text()[1:])
        contents.setVisible(not is_visible)

    def destroy(self, destroyWindow: bool=True, destroySubWindows: bool=True) -> None:
        for s in self.__subscriptions:
            s.dispose()
        return super().destroy(destroyWindow, destroySubWindows)


from PySide6 import QtCore, QtGui, QtWidgets

from stfed.view.autogenerated.Ui_MifResourcePreview import Ui_MifResourcePreview
from stfed.repos.preview_images import preview_images_repo_instance
from stfed.repos.resources import resources_repo_instance as resources_repo
import stfed.factories.ani
import stfed.factories.mif
import stfed.factories.pal
import stfed.factories.tlb
import stfed.model
import stfed.repos.preview_images
from stfed.repos.user_preferences import repo as user_preferences_repo
import stfed.services.unit_colors
import stfed.view.ThreadWrapper

class MifResourcePreview(QtWidgets.QWidget, Ui_MifResourcePreview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.unitlib_lines.setVisible(False)

        self.__pixmap = None
        self.__zoom = 1
        self.__subscriptions = []

        self.unitlib_toggle.clicked.connect(self.__unitlib_toggle_clicked)
        self.units_toggle.clicked.connect(self.__units_toggle_clicked)
        self.misc_toggle.clicked.connect(self.__misc_toggle_clicked)
        self.items_toggle.clicked.connect(self.__items_toggle_clicked)
        self.__subscriptions.append(
            user_preferences_repo.values().map_subscribe(
                lambda p: p.double_width_image_preview,
                self.__on_double_width_preview_pref_changed))

    
    def set_model(self, mif_resource: stfed.model.Resource):
        pal_rn = mif_resource.resource_name //10 * 10 - 10
        pal = self.__get_palette_or_fallback(pal_rn)
        substitute_pal = self.__get_palette_or_fallback(9101)
        side1_color = stfed.model.UnitColors.RED
        side2_color = stfed.model.UnitColors.BLUE
        if mif_resource.resource_name % 10 == 0:
            side1_color, side2_color = side2_color, side1_color
        pal_with_colors = stfed.services.unit_colors.substitute_unit_colors(pal, side1_color, side2_color, substitute_pal)

        tlb_rn = pal_rn
        tlb_resource = resources_repo.get(tlb_rn, stfed.model.ResourceType.TLB)
        tlb = stfed.factories.tlb.parse_tile_library(tlb_resource.data())
        mif = stfed.factories.mif.parse_map_info_res(mif_resource.data())

        unitlib_dict = {}
        for unitlib_entry in mif.unitlib:
            if unitlib_entry.base_anim == 0:
                continue
            # base_anim is walking south, +20 is idle
            # TODO: refactor away and check sprite by sprite, gnomes and clerics are broken, others might be too
            idle_anim = unitlib_entry.base_anim + 20
            # golems
            if unitlib_entry.base_anim == 500:
                idle_anim = 398
            # roc egg entry points to the portrait
            elif unitlib_entry.base_anim == 2593:
                idle_anim = 384
            ani_resource = resources_repo.get(idle_anim, stfed.model.ResourceType.ANI)
            if ani_resource is None:
                continue
            unitlib_dict[unitlib_entry.internal_name] = stfed.factories.ani.parse(ani_resource)

        itemlib = {}
        RESOURCES_ITEMS_START = 2500
        for item_type in stfed.model.ItemType:
            res = resources_repo.get(RESOURCES_ITEMS_START + (item_type.value - 1)*2, stfed.model.ResourceType.ANI)
            if res is None:
                continue
            itemlib[item_type] = stfed.factories.ani.parse(res)
            

        # content = preview_images_repo_instance.get(
        #     mif_resource.source_file,
        #     mif_resource.resource_name,
        #     mif_resource.resource_type)
        # if content is None:
        #     content = stfed.factories.mif.export_preview_image(
        #         mif,
        #         tlb,
        #         pal_with_colors,
        #         unitlib,
        #         itemlib)
        #     preview_images_repo_instance.put(
        #         mif_resource.source_file,
        #         mif_resource.resource_name,
        #         mif_resource.resource_type,
        #         content)

        # pixmap = QtGui.QPixmap()
        # pixmap.loadFromData(content, 'PNG')
        # self.__pixmap = pixmap

        # adj = 2 if user_preferences_repo.get().double_width_image_preview else 1
        # pixmap = pixmap.scaled(pixmap.width() * adj * self.__zoom, pixmap.height() * self.__zoom)
        # self.map_preview.setPixmap(pixmap)

        random_items_img = stfed.factories.mif.export_random_items_preview(mif, pal, itemlib)
        if random_items_img is not None:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(random_items_img, 'PNG')
            self.random_items_img.setPixmap(pixmap)
        self.random_items_label.setVisible(random_items_img is not None)
        
        units_start = mif.config_lines.index("#UNITS")
        units_end = [
            i
            for i, line in enumerate(mif.config_lines)
            if i > units_start
            if not line.startswith("# ") and not line == '#RANDUNITS'
        ][0]
        items_start = mif.config_lines.index("#ITEMS")

        unitlib = mif.config_lines[:units_start]
        units = mif.config_lines[units_start:units_end]
        misc = mif.config_lines[units_end:items_start]
        items = mif.config_lines[items_start:]

        self.unitlib_lines.setText("\n".join(unitlib))
        self.unit_lines.setText("\n".join(units))
        self.misc_lines.setText("\n".join(misc))
        self.item_lines.setText("\n".join(items))

        headers = ["Id", "Function", "Position", "Destination", "Owner", "Max HP", "Preset item", "Hot spot", "Pick random item", "Special item drop"]
        self.spaces_table.setColumnCount(len(headers))
        self.spaces_table.setHorizontalHeaderLabels(headers)
        self.spaces_table.setRowCount(0)
        self.spaces_table.setRowCount(len(mif.spaces))
        for rowid, space in enumerate(mif.spaces):
            self.spaces_table.setItem(rowid, 0, QtWidgets.QTableWidgetItem(str(rowid)))
            self.spaces_table.setItem(rowid, 1, QtWidgets.QTableWidgetItem(space.func_type.name))
            self.spaces_table.setItem(rowid, 2, QtWidgets.QTableWidgetItem(f"{(space.x_pos, space.y_pos)}"))
            self.spaces_table.setItem(rowid, 3, QtWidgets.QTableWidgetItem(f"{(space.dest_x, space.dest_y)}"))
            self.spaces_table.setItem(rowid, 4, QtWidgets.QTableWidgetItem(space.owner.name))
            self.spaces_table.setItem(rowid, 5, QtWidgets.QTableWidgetItem(str(space.max_hp)))
            self.spaces_table.setItem(rowid, 6, QtWidgets.QTableWidgetItem(space.preset_item.name if space.preset_item is not None else ""))
            self.spaces_table.setItem(rowid, 7, QtWidgets.QTableWidgetItem("Y" if space.hot_spot else "N"))
            self.spaces_table.setItem(rowid, 8, QtWidgets.QTableWidgetItem("Y" if space.pick_random_item else "N"))
            self.spaces_table.setItem(rowid, 9,QtWidgets.QTableWidgetItem( "Y" if space.special_item_drop else "N"))
        self.spaces_table.resizeRowsToContents()
        self.spaces_table.resizeColumnsToContents()


        def generate_images(progress_signal):
            progress_signal.emit(0, "Generating preview ...")
            content = preview_images_repo_instance.get(
                mif_resource.source_file,
                mif_resource.resource_name,
                mif_resource.resource_type)
            if content is None:
                content = stfed.factories.mif.export_preview_image(
                    mif,
                    tlb,
                    pal_with_colors,
                    unitlib_dict,
                    itemlib)
                preview_images_repo_instance.put(
                    mif_resource.source_file,
                    mif_resource.resource_name,
                    mif_resource.resource_type,
                    content)

            
            progress_signal.emit(1, "Done")

        def on_images_generated():
            self.__dialog.close()
            self.__dialog = None
            content = preview_images_repo_instance.get(
                mif_resource.source_file,
                mif_resource.resource_name,
                mif_resource.resource_type)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(content, 'PNG')
            self.__pixmap = pixmap

            adj = 2 if user_preferences_repo.get().double_width_image_preview else 1
            pixmap = pixmap.scaled(pixmap.width() * adj * self.__zoom, pixmap.height() * self.__zoom)
            self.map_preview.setPixmap(pixmap)


        self.__dialog = stfed.view.BackgroundOperationWindow.BackgroundOperationWindow()
        self.__dialog.show()
        self.background_operation = stfed.view.ThreadWrapper.ThreadWrapper(generate_images)
        self.background_operation.finished.connect(on_images_generated)
        self.background_operation.on_progress.connect(self.__dialog.set_progress)
        self.background_operation.start()


    def __toggle(self, header: QtWidgets.QPushButton, contents: QtWidgets.QWidget):
        is_visible = contents.isVisible()
        new_icon = '-' if is_visible else '+'
        header.setText(new_icon + header.text()[1:])
        contents.setVisible(not is_visible)


    def __unitlib_toggle_clicked(self):
        self.__toggle(self.unitlib_toggle, self.unitlib_lines)


    def __units_toggle_clicked(self):
        self.__toggle(self.units_toggle, self.unit_lines)


    def __misc_toggle_clicked(self):
        self.__toggle(self.misc_toggle, self.misc_lines)


    def __items_toggle_clicked(self):
        self.__toggle(self.items_toggle, self.item_lines)


    def __on_double_width_preview_pref_changed(self, new_value: bool):
        if self.__pixmap is None:
            return
        adj = 2 if new_value else 1
        pixmap = self.__pixmap
        pixmap = pixmap.scaled(pixmap.width() * adj * self.__zoom, pixmap.height() * self.__zoom)
        self.map_preview.setPixmap(pixmap)

    def __get_palette_or_fallback(self, rn: int) -> stfed.model.Palette:
        pal_resource = resources_repo.get(rn, stfed.model.ResourceType.PAL)
        if pal_resource is not None:
            pal = stfed.factories.pal.parse(pal_resource.data())
        else:
            pal = stfed.model.Palette([(i, i, i) for i in range(256)])
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setText(f"Could not find the corresponding palette {rn}.PAL, falling back to monochrome instead.")
            msgBox.setWindowTitle("Error")
            msgBox.exec()
        return pal


    def destroy(self, destroyWindow: bool=True, destroySubWindows: bool=True) -> None:
        for s in self.__subscriptions:
            s.unsubscribe()
        return super().destroy(destroyWindow, destroySubWindows)
 
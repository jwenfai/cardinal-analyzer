"""
waitingspinnerwidget from https://github.com/z3ntu/QtWaitingSpinner
code in main.py, wizardUI.py etc. adapted from https://github.com/jddinneen/cardinal
"""

import os
import json
import _pickle
import traceback
from pathlib import Path
from PyQt5.QtCore import (
    Qt, pyqtSlot, pyqtSignal, QObject, QRunnable, QThreadPool)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon
from PyQt5.QtWidgets import (
    QWizard, QWidget, QPushButton, QApplication, QFileDialog, QGridLayout,
    QLabel,  QTreeView, QHeaderView, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QSplitter, QVBoxLayout)
from waitingspinnerwidget import QtWaitingSpinner
from wizardUI import WizardUI
from drive_analyzer import (
    record_stat, compute_stat, anonymize_stat, drive_measurement,
    check_collection_properties)


def path_str(root_path):
    """ Converts path to string, returns '' if path is None """
    if root_path is None:
        return ''
    elif isinstance(root_path, Path):
        return str(root_path)
    else:
        raise TypeError('Invalid type used for root_path, '
                        'should be pathlib.Path or NoneType')


# TODO: Fix: simplify_tree crashes when all folders do not contain a single
# file due to dir_dict being empty
class WorkerSignals(QObject):
    started = pyqtSignal()
    result = pyqtSignal(object)
    finished = pyqtSignal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.signals.started.emit()
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class Main(QWizard):
    def __init__(self):
        super(Main, self).__init__()

        # build UI
        self.ui = WizardUI()
        self.ui.setup_ui(self)
        self.root_path_0 = None
        # self.root_path_0 = Path('~/Dropbox/academic').expanduser()

        # connect signals
        self.threadpool = QThreadPool()
        self.expanded_items_list_0 = []
        # self.unchecked_items_set_0 = set()
        # self.renamed_items_dict_0 = dict()

        self.demo_dir_dict = {1: {'dirname': 'hello', 'cumfiles': 123, 'childkeys': [2]},
                              2: {'dirname': 'world', 'cumfiles': 45, 'childkeys': [3, 4]},
                              3: {'dirname': 'one', 'cumfiles': 6, 'childkeys': []},
                              4: {'dirname': 'two', 'cumfiles': 7, 'childkeys': []}, }
        self.og_dir_dict_0, self.anon_dir_dict_0 = dict(), dict()
        self.folder_edit_0 = QLabel()
        self.folder_edit_0.setText(path_str(self.root_path_0))

        self.ui.select_btn_0.clicked.connect(self.show_file_dialog_0)
        self.ui.save_btn_0.clicked.connect(self.save_collected_data_0)

        og_model_headers = ['Folder Name', 'Accessible Files', 'Accessible Files (Recalculated)']
        # Initialize model and tree for root 0
        self.og_model_0 = QStandardItemModel()
        self.ui.og_tree_0.setModel(self.og_model_0)
        self.ui.og_tree_0.setSortingEnabled(True)
        self.og_model_0.setHorizontalHeaderLabels(og_model_headers)
        self.og_root_item_0 = self.og_model_0.invisibleRootItem()
        # self.refresh_treeview(self.og_model_0, self.ui.og_tree_0, self.og_dir_dict_0)
        self.refresh_treeview(self.og_model_0, self.ui.og_tree_0, self.demo_dir_dict)
        self.og_model_0.itemChanged.connect(self.on_item_change_0)

        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.spinner.setRoundness(70.0)
        self.spinner.setMinimumTrailOpacity(15.0)
        self.spinner.setTrailFadePercentage(70.0)
        self.spinner.setNumberOfLines(12)
        self.spinner.setLineLength(30)
        self.spinner.setLineWidth(10)
        self.spinner.setInnerRadius(15)
        self.spinner.setRevolutionsPerSecond(1)

    def refresh_treeview(self, model, tree, dir_dict,
                         checkable=True, anon_tree=False):
        model.removeRow(0)
        root_item = model.invisibleRootItem()
        # dir_dict key starts at 1 since 0==False
        self.append_all_children(1, dir_dict, root_item, checkable, anon_tree)
        tree.expandToDepth(0)
        self.header_autoresizable(tree.header())

    def append_all_children(self, dirkey, dir_dict, parent_item,
                            checkable=True, anon_tree=False):
        if dirkey in dir_dict:
            dirname = QStandardItem(dir_dict[dirkey]['dirname'])
            cumfiles = QStandardItem(str(dir_dict[dirkey]['cumfiles']))
            cumfiles2 = QStandardItem(str(dir_dict[dirkey]['cumfiles']))
            # dirname_edited = QStandardItem(dir_dict[dirkey]['dirname'])
            # nfiles = QStandardItem(str(dir_dict[dirkey]['nfiles']))
            # if anon_tree:
            #     items = [dirname, cumfiles]
            # else:
            #     items = [dirname, dirname_edited, cumfiles]
            items = [dirname, cumfiles, cumfiles2]
            dirname.setData(dirkey, Qt.UserRole)
            # dirname_edited.setData(dirkey, Qt.UserRole)
            if checkable:
                dirname.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
                    Qt.ItemIsUserCheckable)
                dirname.setCheckState(Qt.Checked)
                cumfiles.setFlags(Qt.ItemIsEnabled)
                cumfiles2.setFlags(Qt.ItemIsEnabled)
                # dirname_edited.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
                # nfiles.setFlags(Qt.ItemIsEnabled)
            parent_item.appendRow(items)
            child_ix = parent_item.rowCount() - 1
            parent_item = parent_item.child(child_ix)
            children_keys = dir_dict[dirkey]['childkeys']
            for child_key in sorted(children_keys):
                self.append_all_children(child_key, dir_dict, parent_item,
                                         checkable, anon_tree)

    def on_item_change_0(self, item):
        if item.column() == 0:
            dirkey = item.data(Qt.UserRole)
            if (item.rowCount() == 0
                    and item.checkState() == Qt.PartiallyChecked):
                item.setCheckState(Qt.Checked)
            item_checkstate = item.checkState()
            parent_item = item.parent()
            if parent_item is None:
                nchild = item.rowCount()
                if nchild > 0:
                    for child_ix in range(nchild):
                        self.propagate_checkstate_child(
                            item, child_ix, item_checkstate)
            if parent_item is not None:
                child_ix = item.row()
                self.propagate_checkstate_child(
                    parent_item, child_ix, item_checkstate)
                self.propagate_checkstate_parent(
                    item, item_checkstate)
        #     if item_checkstate == Qt.Unchecked:
        #         self.unchecked_items_set_0.add(dirkey)
        #     elif item_checkstate in (Qt.Checked, Qt.PartiallyChecked):
        #         if dirkey in self.unchecked_items_set_0:
        #             self.unchecked_items_set_0.remove(dirkey)
        # if item.column() == 1:
        #     dirkey = item.data(Qt.UserRole)
        #     self.renamed_items_dict[dirkey] = item.text()
        # self.preview_btn.setEnabled(True)
        # self.save_btn.setDisabled(True)

    def propagate_checkstate_child(
            self, parent_item, child_ix, parent_checkstate):
        """ If parent has a full checkmark, make sure all the children's
        checkboxes are ticked as well. """
        if parent_checkstate != Qt.PartiallyChecked:
            parent_item.child(child_ix).setCheckState(parent_checkstate)
            parent_item = parent_item.child(child_ix)
            nchild = parent_item.rowCount()
            if nchild > 0:
                for child_ix in range(nchild):
                    self.propagate_checkstate_child(
                        parent_item, child_ix, parent_checkstate)

    def propagate_checkstate_parent(self, item, item_checkstate):
        """ If some children are unchecked, make parent partially checked.
        If all children are checked, give parent a full checkmark. """
        parent_item = item.parent()
        if parent_item is not None:
            if self.all_sibling_checked(item):
                parent_item.setCheckState(Qt.Checked)
            if (item_checkstate in (Qt.Checked, Qt.PartiallyChecked)
                    and parent_item.checkState() == Qt.Unchecked):
                parent_item.setCheckState(Qt.PartiallyChecked)
            if (item_checkstate in (Qt.Unchecked, Qt.PartiallyChecked)
                    and parent_item.checkState() == Qt.Checked):
                parent_item.setCheckState(Qt.PartiallyChecked)

    def all_sibling_checked(self, item):
        """ Determine if siblings (items sharing the same parent and are on
        the same tree level) are all checked. """
        all_checked = True
        if item.parent() is not None:
            parent_item = item.parent()
            nchild = parent_item.rowCount()
            for child_ix in range(nchild):
                if parent_item.child(child_ix).checkState() in (
                        Qt.Unchecked, Qt.PartiallyChecked):
                    all_checked = False
                    break
        return all_checked








    def propagate_cumfiles(
            self, item, initiator_checkstate=None, initiator_diff=None):
        """
        *****************Untested!!!********************
        Update cumulative file counts
        initiator_checkstate: checkstate of the first item that was
        checked/unchecked that prompted the whole cascade
        initiator_diff: the difference in file count values that will be
        propagated unchanged
        """
        # item_row = item.row()
        # print(item.row(), item.column(), -int(self.og_model_0.item(item_row, 2).text()))
        # print(str(int(self.og_model_0.item(1, 1).text())-8))
        # print(self.og_model_0.item(0, 0).child(0, 0).row(), self.og_model_0.item(0, 0).child(0, 0).text())
        # self.og_model_0.setItem(1, 0, QStandardItem('hello'))

        # item_row = item.row()
        # parent_item = item.parent()
        # if parent_item:
        #     print(item_row, parent_item.text())
        #     parent_item.setChild(item_row, 2, QStandardItem('yeet'))

        # item = QStandardItem('helloworld')

        item_row = item.row()
        parent_item = item.parent()
        if initiator_checkstate is None:
            initiator_checkstate = item.checkState()
        if parent_item is not None:
            parent_row = parent_item.row()
            grandparent_item = parent_item.parent()
            if initiator_diff is None:
                if initiator_checkstate == Qt.Unchecked:
                    # pass
                    initiator_diff = -int(parent_item.child(item_row, 2).text())
                elif initiator_checkstate == Qt.Checked:
                    # pass
                    initiator_diff = int(parent_item.child(item_row, 2).text())
            if grandparent_item is not None:
                grandparent_item.child(parent_row, 2).setText(str(
                    int(grandparent_item.child(parent_row, 2).text()) +
                    initiator_diff))
            print(item.text(), initiator_diff)
            self.propagate_cumfiles(
                parent_item, initiator_checkstate, initiator_diff)

        # item_row = item.row()
        # parent_item = item.parent()
        # parent_row = parent_item.row()
        # # parent_dirkey = parent_item.data(Qt.UserRole)
        # if initiator_checkstate is None:
        #     initiator_checkstate = item.checkState()
        # if parent_item is not None:
        #     if initiator_diff is None:
        #         if initiator_checkstate == Qt.Unchecked:
        #             # initiator_diff = -dir_dict[dirkey]['cumfiles']
        #             initiator_diff = -int(self.og_model_0.item(item_row, 2).text())
        #         elif initiator_checkstate == Qt.Checked:
        #             # initiator_diff = dir_dict[dirkey]['cumfiles']
        #             initiator_diff = int(self.og_model_0.item(item_row, 2).text())
        #     # dir_dict[parent_dirkey]['cumfiles'] += initiator_diff
        #     self.og_model_0.item(parent_row, 2).setText(str(
        #         int(self.og_model_0.item(parent_row, 2).text()) +
        #         initiator_diff))
        #     self.propagate_cumfiles(
        #         parent_item, initiator_checkstate, initiator_diff)
        #     # also need to update dir_dict, not just GUI

    # def exclusion_logic(self):
    #     if excluded is True:
    #         item.checkState() = Qt.Unchecked  # if excluded,
    #         item.setFlags(Qt.ItemIsUserTristate)  # if excluded, user cannot check item until 'exclusion' is unchecked
    #     if excluded is False:
    #         item.setFlags(
    #             Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
    #             Qt.ItemIsUserCheckable)
    #         # dirname.setFlags(
    #         #     Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
    #         #     Qt.ItemIsUserCheckable)
















    def build_tree_structure_threaded_0(self, root_path):
        worker = Worker(record_stat, root_path)
        worker.signals.started.connect(self.build_tree_started_0)
        worker.signals.result.connect(self.build_tree_finished_0)
        self.threadpool.start(worker)

    def build_tree_started_0(self):
        """ Status messages when building a tree should be placed here. """
        self.expanded_items_list_0 = []
        # self.unchecked_items_set_0 = set()
        # self.renamed_items_dict_0 = dict()
        self.spinner.start()
        print('build tree started')

    def build_tree_finished_0(self, result):
        """ Status messages when tree building is complete should be
        placed here. """
        self.og_dir_dict_0 = result
        self.og_dir_dict_0 = compute_stat(self.og_dir_dict_0)
        self.refresh_treeview(self.og_model_0, self.ui.og_tree_0, self.og_dir_dict_0)
        self.ui.save_btn_0.setEnabled(True)
        self.spinner.stop()
        print('build tree stopped')

    def show_file_dialog_0(self):
        dirpath = QFileDialog.getExistingDirectory(
            self, 'Select Folder', path_str(self.root_path_0))
        if dirpath:
            self.root_path_0 = Path(dirpath)
            print('path returned')
            self.folder_edit_0.setText(path_str(self.root_path_0))
            print('path text set')
            self.build_tree_structure_threaded_0(self.root_path_0)
            # self.ui.save_btn_0.setEnabled(True)
        else:
            self.clear_root()
            self.ui.save_btn_0.setDisabled(True)

    def save_collected_data_0(self):
        formats = "JavaScript Object Notation (*.json)"
        filename, extension = QFileDialog.getSaveFileName(
            self, 'Save File', 'my_folder_data.json', formats)
        # print(filename, extension)
        if filename != '':
            # self.anon_dir_dict_0 = {1: 2, 3: 4}
            with open(filename, 'w', encoding='utf8') as file:
                json.dump(self.anon_dir_dict_0, file, ensure_ascii=False, indent=4)

    def clear_root(self):
        self.root_path_0 = None
        self.og_dir_dict_0 = dict()
        # self.unchecked_items_set_0 = set()
        # self.renamed_items_dict_0 = dict()
        self.folder_edit_0.setText(path_str(self.root_path_0))
        self.og_model_0.removeRow(0)

    @staticmethod
    def header_autoresizable(header):
        """ Resize all sections to content and user interactive,
        see https://centaurialpha.github.io/resize-qheaderview-to-contents-and-interactive
        """

        for column in range(header.count()):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
            width = header.sectionSize(column)
            header.setSectionResizeMode(column, QHeaderView.Interactive)
            header.resizeSection(column, width)

# the whole app
if __name__ == '__main__':
    import sys
    # app = QApplication(sys.argv)
    app = QApplication([])
    main = Main()
    main.show()
    sys.exit(app.exec_())

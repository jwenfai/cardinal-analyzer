"""
waitingspinnerwidget from https://github.com/z3ntu/QtWaitingSpinner
code in main.py, wizardUI.py etc. adapted from https://github.com/jddinneen/cardinal
"""

import json
import _pickle
import traceback
from pathlib import Path
from PyQt5.QtCore import (
    Qt, pyqtSlot, pyqtSignal, QObject, QRunnable, QThreadPool, QDateTime)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextDocument
from PyQt5.QtWidgets import QWizard, QApplication, QFileDialog, QHeaderView
from waitingspinnerwidget import QtWaitingSpinner
from wizardUI import WizardUI
from drive_analyzer import (
    record_stat, compute_stat, json_serializable, dict_readable)


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

        # connect signals
        self.threadpool = QThreadPool()

        self.keytree_dir_dict = {
            1: {'dirname': 'Home', 'dirparent': False, 'nfiles': 78, 'cumfiles': 123,
                'childkeys': {2}, 'mtime': 1330884000.0, 'selection_state': 1, 'exclusion_state': 0,
                'description': "Partial: some contents (files and/or folders) are relevant to the collection"},
            2: {'dirname': 'Work files', 'dirparent': 1, 'nfiles': 32, 'cumfiles': 45,
                'childkeys': {3, 4}, 'mtime': 1330797600.0, 'selection_state': 1, 'exclusion_state': 0,
                'description': "Partial: some contents (files and/or folders) are relevant to the collection"},
            3: {'dirname': 'Travel photos', 'dirparent': 2, 'nfiles': 6, 'cumfiles': 6,
                'childkeys': set(), 'mtime': 1330624800.0, 'selection_state': 0, 'exclusion_state': 0,
                'description': "Unchecked: this folder is simply not relevant to the collection"},
            4: {'dirname': 'Project A', 'dirparent': 2, 'nfiles': 1, 'cumfiles': 7,
                'childkeys': {5, 6}, 'mtime': 1325527200.0, 'selection_state': 2, 'exclusion_state': 0,
                'description': "Checked: this folder is relevant to the collection"},
            5: {'dirname': 'Drafts', 'dirparent': 4, 'nfiles': 2, 'cumfiles': 2,
                'childkeys': set(), 'mtime': 1255891200.0, 'selection_state': 2, 'exclusion_state': 0,
                'description': "Checked: this folder is relevant to the collection"},
            6: {'dirname': 'Bank transfer', 'dirparent': 4, 'nfiles': 4, 'cumfiles': 4,
                'childkeys': set(), 'mtime': 1322202000.0, 'selection_state': 0, 'exclusion_state': 2,
                'description': "Excluded: this folder is excluded (e.g., it contains sensitive information/work)"},
        }

        self.demo_dir_dict = {
            1: {'dirname': 'folder 1', 'dirparent': False, 'nfiles': 78, 'cumfiles': 123,
                'childkeys': {2}, 'mtime': 1330884000.0, 'selection_state': None, 'exclusion_state': None},
            2: {'dirname': 'folder 2', 'dirparent': 1, 'nfiles': 32, 'cumfiles': 45,
                'childkeys': {3, 4}, 'mtime': 1330797600.0, 'selection_state': None, 'exclusion_state': None},
            3: {'dirname': 'folder 3', 'dirparent': 2, 'nfiles': 6, 'cumfiles': 6,
                'childkeys': set(), 'mtime': 1330624800.0, 'selection_state': None, 'exclusion_state': None},
            4: {'dirname': 'folder 4', 'dirparent': 2, 'nfiles': 1, 'cumfiles': 7,
                'childkeys': {5, 6}, 'mtime': 1325527200.0, 'selection_state': None, 'exclusion_state': None},
            5: {'dirname': 'folder 5', 'dirparent': 4, 'nfiles': 2, 'cumfiles': 2,
                'childkeys': set(), 'mtime': 1255891200.0, 'selection_state': None, 'exclusion_state': None},
            6: {'dirname': 'folder 6', 'dirparent': 4, 'nfiles': 4, 'cumfiles': 4,
                'childkeys': set(), 'mtime': 1322202000.0, 'selection_state': None, 'exclusion_state': None},
        }

        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.spinner.setRoundness(70.0)
        self.spinner.setMinimumTrailOpacity(15.0)
        self.spinner.setTrailFadePercentage(70.0)
        self.spinner.setNumberOfLines(12)
        self.spinner.setLineLength(30)
        self.spinner.setLineWidth(10)
        self.spinner.setInnerRadius(15)
        self.spinner.setRevolutionsPerSecond(1)

        keytree = KeyTreeOperations(
            self.ui.og_tree_key, self.threadpool, self.spinner)
        tree0 = TreeOperations(
            self.ui.og_tree_0, self.threadpool, self.spinner)
        tree1 = TreeOperations(
            self.ui.og_tree_1, self.threadpool, self.spinner,
            self.ui.select_btn_1, self.ui.save_btn_1, self.ui.load_btn_1, self.ui.less_btn_1)

        keytree.load_dir_dicts(self.keytree_dir_dict, checkable=False, expand_all=True)
        tree0.load_dir_dicts(self.demo_dir_dict, expand_all=True)
        self.ui.reset_demo_btn.clicked.connect(
            lambda: tree0.refresh_treeview(tree0.og_model, tree0.og_tree, self.demo_dir_dict, expand_all=True))
        tree1.select_btn.clicked.connect(lambda: self.select_tree_root(tree1))
        tree1.save_btn.clicked.connect(lambda: self.save_collected_data(tree1))
        tree1.load_btn.clicked.connect(lambda: self.load_collected_data(tree1))
        tree1.less_btn.clicked.connect(lambda: self.expand_to_depth(tree1, 0))
        self.ui.consent_savebutton.clicked.connect(self.save_consent)
        self.ui.wizardpage1.registerField("consentbox*", self.ui.consentbox)

    def select_tree_root(self, tree):
        dirpath = QFileDialog.getExistingDirectory(
            self, 'Select Folder', path_str(tree.root_path))
        if dirpath:
            tree.root_path = Path(dirpath)
            tree.build_tree_structure_threaded(tree.root_path)
        else:
            tree.clear_root()
            tree.save_btn.setDisabled(True)
            tree.less_btn.setDisabled(True)

    def save_consent(self):
        formats = "Text (*.txt)"
        filename, extension = QFileDialog.getSaveFileName(
            self, 'Save File', path_str(Path('~').expanduser() / 'my_consent.txt'), formats)
        if filename != '':
            with open(filename, 'w', encoding='utf8') as file:
                consent_txt = (self.ui.welcomelabel.text() +
                               self.ui.consentbox.text() +
                               self.ui.reblabel.text())
                doc = QTextDocument()
                doc.setHtml(consent_txt)
                consent_plaintext = doc.toPlainText()
                file.write(consent_plaintext)

    def make_super_dict(self, dict_list, name_list):
        super_dict = dict()
        if len(dict_list) == len(name_list):
            for dict_, name in zip(dict_list, name_list):
                super_dict[name] = dict_
            return super_dict
        else:
            print('Mismatch in number of dicts and supplied names.')

    def save_collected_data(self, tree):
        formats = "JavaScript Object Notation (*.json)"
        filename, extension = QFileDialog.getSaveFileName(
            self, 'Save File', path_str(Path('~').expanduser() / 'my_folder_data.json'), formats)
        if filename != '':
            anon_dir_dict = _pickle.loads(_pickle.dumps(tree.og_dir_dict))
            tree.save_checkstates_root(anon_dir_dict)
            json_serializable(anon_dir_dict)
            super_dict = self.make_super_dict(
                [anon_dir_dict, self.ui.textarea_wp3_0.toPlainText()],
                ['dir_dict', 'software_choice'])
            with open(filename, 'w', encoding='utf8') as file:
                json.dump(super_dict, file, indent=4)

    def load_collected_data(self, tree):
        formats = "JavaScript Object Notation (*.json)"
        filename, extension = QFileDialog.getOpenFileName(
            self, 'Load File', path_str(Path('~').expanduser()), formats)
        if filename != '':
            with open(filename, 'r', encoding='utf8') as file:
                super_dict = json.load(file)
                self.ui.textarea_wp3_0.setPlainText(super_dict['software_choice'])
                tree.og_dir_dict = super_dict['dir_dict']
                dict_readable(tree.og_dir_dict)
                tree.anon_dir_dict = _pickle.loads(_pickle.dumps(tree.og_dir_dict))
                tree.refresh_treeview(tree.og_model, tree.og_tree, tree.og_dir_dict)
                tree.save_btn.setEnabled(True)
                tree.less_btn.setEnabled(True)

    def expand_to_depth(self, tree, depth):
        tree.og_tree.expandToDepth(depth)


class QStandardNumItem(QStandardItem):
    def __lt__(self, other):
        return int(self.text()) < int(other.text())


class TreeOperations:
    """Some functions are specific to a particular root/tree model. Placing
    these and other functions into their own class helps avoid near-duplicate
    function definitions with minor variable changes, hopefully making
    debugging easier."""
    def __init__(self, og_tree, threadpool, spinner,
                 select_btn=None, save_btn=None, load_btn=None, less_btn=None):
        og_model_headers = ['Folder Name', 'Exclude', 'Accessible Files',
                            'Date Modified']
        self.unchecked_items_set = set()
        self.expanded_items_list = []
        self.threadpool = threadpool
        self.spinner = spinner
        self.root_path = Path('~').expanduser()
        self.select_btn = select_btn
        self.save_btn = save_btn
        self.load_btn = load_btn
        self.less_btn = less_btn

        # Initialize model and tree
        self.og_tree = og_tree
        self.og_dir_dict, self.anon_dir_dict = dict(), dict()
        self.og_model = QStandardItemModel()
        self.og_tree.setModel(self.og_model)
        self.og_tree.setSortingEnabled(True)
        self.og_model.setHorizontalHeaderLabels(og_model_headers)
        self.refresh_treeview(self.og_model, self.og_tree, self.og_dir_dict)
        self.og_model.itemChanged.connect(self.on_item_change)
        self.og_tree.expanded.connect(lambda: self.header_autoresizable(self.og_tree.header()))

    def refresh_treeview(self, model, tree, dir_dict,
                         checkable=True, anon_tree=False, expand_all=False):
        model.removeRow(0)
        root_item = model.invisibleRootItem()
        # convention: dir_dict key starts at 1 since 0==False
        if len(dir_dict.keys()) > 0:
            first_dirkey = min(dir_dict.keys())
        else:
            first_dirkey = 1
        self.append_all_children(first_dirkey, dir_dict, root_item, checkable, anon_tree)
        if expand_all:
            tree.expandToDepth(1000)
            # 1000 is arbitrary number, using .expandAll() causes children duplication bug
        else:
            tree.expandToDepth(0)
        # sort by first column (folder name) every time tree is built/rebuilt
        tree.sortByColumn(0, Qt.AscendingOrder)
        self.header_autoresizable(tree.header())

    def append_all_children(self, dirkey, dir_dict, parent_item,
                            checkable=True, anon_tree=False):
        if dirkey in dir_dict:
            dirname = QStandardItem(dir_dict[dirkey]['dirname'])
            cumfiles = QStandardNumItem(str(dir_dict[dirkey]['cumfiles']))
            exclusion = QStandardItem('')
            mtime = self.find_mtime(dirkey, dir_dict)
            items = [dirname, exclusion, cumfiles, mtime]
            dirname.setData(dirkey, Qt.UserRole)
            if checkable is True:
                dirname.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
                    Qt.ItemIsUserCheckable)
                exclusion.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
                    Qt.ItemIsUserCheckable)
                cumfiles.setFlags(Qt.ItemIsEnabled)
            elif checkable is False:
                dirname.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate)
                exclusion.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate)
                cumfiles.setFlags(Qt.ItemIsEnabled)
            selection_state = dir_dict[dirkey]['selection_state']
            exclusion_state = dir_dict[dirkey]['exclusion_state']
            if selection_state is not None:
                dirname.setCheckState(selection_state)
            else:
                dirname.setCheckState(Qt.Unchecked)
            if exclusion_state is not None:
                exclusion.setCheckState(exclusion_state)
            else:
                exclusion.setCheckState(Qt.Unchecked)
            parent_item.appendRow(items)
            child_ix = parent_item.rowCount() - 1
            parent_item = parent_item.child(child_ix)
            children_keys = dir_dict[dirkey]['childkeys']
            for child_key in sorted(children_keys):
                self.append_all_children(child_key, dir_dict, parent_item,
                                         checkable, anon_tree)

    def on_item_change(self, item):
        root = self.og_model.invisibleRootItem()
        if item.column() == 0:
            dirkey = item.data(Qt.UserRole)
            item_checkstate = item.checkState()
            item_row = item.row()
            if item.parent() is None:
                parent = root
            else:
                parent = item.parent()
            if item.checkState() == Qt.PartiallyChecked:
                if (item.rowCount() == 0
                        or parent.child(item_row, 1).checkState() == Qt.PartiallyChecked):
                    item.setCheckState(Qt.Checked)
            self.propagate_checkstate_child(
                parent, item_row, item_checkstate)
            self.propagate_checkstate_parent(
                item)
            if item_checkstate == Qt.Unchecked:
                self.unchecked_items_set.add(dirkey)
            elif item_checkstate in (Qt.Checked, Qt.PartiallyChecked):
                if dirkey in self.unchecked_items_set:
                    self.unchecked_items_set.remove(dirkey)
            # self.recalculate_cumfiles()
        if item.column() == 1:
            self.dir_exclusion(item, root)

    def find_mtime(self, dirkey, dir_dict):
        # display ISO date only; exclude time
        # time priority:
        # 1. latest edited file's mtime (incl. files in child folders)
        # 2. folder mtime
        # 3. folder atime
        # 4. folder ctime
        # mtime = QStandardItem(QDateTime.fromSecsSinceEpoch(
        #     dir_dict[dirkey]['mtime']).toString(Qt.ISODate)[:-9])

        def valid_value(value):
            if value is not None:
                if value > 0:
                    return value

        def recursive_mtime(dirkey_, dir_dict_, mtime_list):
            if 'filestat' in dir_dict_[dirkey_]:  # filestat absent in demo_dir_dict
                for filestat_ in dir_dict_[dirkey_]['filestat']:
                    if valid_value(filestat_['mtime']):
                        mtime_list.append(filestat_['mtime'])
            for childkey in dir_dict_[dirkey_]['childkeys']:
                recursive_mtime(childkey, dir_dict_, mtime_list)

        file_mtime_list = []
        recursive_mtime(dirkey, dir_dict, file_mtime_list)
        if len(file_mtime_list) > 0:
            mtime = max(file_mtime_list)
        elif len(file_mtime_list) == 0:
            if valid_value(dir_dict[dirkey]['mtime']):
                mtime = dir_dict[dirkey]['mtime']
            else:
                if valid_value(dir_dict[dirkey]['atime']):
                    mtime = dir_dict[dirkey]['atime']
                else:
                    if valid_value(dir_dict[dirkey]['ctime']):
                        mtime = dir_dict[dirkey]['ctime']
        mtime = QStandardItem(QDateTime.fromSecsSinceEpoch(
            mtime).toString(Qt.ISODate)[:-9])
        return mtime

    def recalculate_cumfiles(self):
        replacement_cumfiles_list = []
        root = self.og_model.invisibleRootItem()
        excluded = self.unchecked_items_set
        self.anon_dir_dict = _pickle.loads(_pickle.dumps(self.og_dir_dict))
        for dirkey in sorted(self.anon_dir_dict.keys(), reverse=True):
            childkeys = self.anon_dir_dict[dirkey]['childkeys']
            self.anon_dir_dict[dirkey]['childkeys'] = childkeys.difference(excluded)
            self.anon_dir_dict[dirkey]['cumfiles'] = self.anon_dir_dict[dirkey]['nfiles']
            for childkey in self.anon_dir_dict[dirkey]['childkeys']:
                self.anon_dir_dict[dirkey]['cumfiles'] += self.anon_dir_dict[childkey]['cumfiles']
            replacement_cumfiles_list.append(str(self.anon_dir_dict[dirkey]['cumfiles']))
        replacement_cumfiles_list = replacement_cumfiles_list[::-1]
        counter = 0
        for child_ix in range(root.rowCount()):
            root.child(child_ix, 2).setText(replacement_cumfiles_list[counter])
            counter += 1

    def propagate_checkstate_child(
            self, parent_item, child_ix, parent_checkstate):
        """ If parent has a full checkmark, make sure all the children's
        checkboxes are ticked as well. """
        if parent_checkstate != Qt.PartiallyChecked and parent_item.child(child_ix).isEnabled():
            parent_item.child(child_ix).setCheckState(parent_checkstate)
            parent_item = parent_item.child(child_ix)
            nchild = parent_item.rowCount()
            if nchild > 0:
                for child_ix in range(nchild):
                    self.propagate_checkstate_child(
                        parent_item, child_ix, parent_checkstate)

    def propagate_checkstate_parent(self, item):
        """ If some children are unchecked, make parent partially checked.
        If all children are checked, give parent a full checkmark. """
        item_checkstate = item.checkState()
        parent_item = item.parent()
        if parent_item is not None:
            if self.all_siblings_checked(item):
                parent_item.setCheckState(Qt.Checked)
            if (item_checkstate in (Qt.Checked, Qt.PartiallyChecked)
                    and parent_item.checkState() == Qt.Unchecked):
                parent_item.setCheckState(Qt.PartiallyChecked)
            if (item_checkstate in (Qt.Unchecked, Qt.PartiallyChecked)
                    and parent_item.checkState() == Qt.Checked
                    # only account for non-excluded items
                    and parent_item.child(item.row(), 1).checkState() in (
                            Qt.Unchecked, Qt.PartiallyChecked)):
                parent_item.setCheckState(Qt.PartiallyChecked)

    def all_siblings_checked(self, item):
        """ Determine if siblings (items sharing the same parent and are on
        the same tree level) are all checked. """
        all_checked = True
        if item.parent() is not None:
            parent_item = item.parent()
            nchild = parent_item.rowCount()
            for child_ix in range(nchild):
                # only account for non-excluded items
                if parent_item.child(child_ix, 1).checkState() in (
                        Qt.Unchecked, Qt.PartiallyChecked):
                    if parent_item.child(child_ix).checkState() in (
                            Qt.Unchecked, Qt.PartiallyChecked):
                        all_checked = False
                        break
        return all_checked

    def dir_exclusion(self, item, root):
        """ if directory is excluded, user cannot check directory until
        'exclusion' is unchecked """
        item_row = item.row()
        exclusion_checkstate = item.checkState()
        if item.parent() is not None:
            parent = item.parent()
        else:
            parent = root
        item = parent.child(item_row, 0)
        if exclusion_checkstate == Qt.Unchecked:
            exclusion_flags = Qt.ItemIsEnabled | Qt.ItemIsUserTristate | Qt.ItemIsUserCheckable
            dir_checkstate = Qt.Checked
            dir_flags = exclusion_flags
            item.setFlags(dir_flags)
            item.setCheckState(dir_checkstate)
            for child_ix in range(item.rowCount()):
                item.child(child_ix, 1).setCheckState(exclusion_checkstate)
                item.child(child_ix, 1).setFlags(exclusion_flags)
        elif exclusion_checkstate == Qt.PartiallyChecked:
            if item.rowCount() == 0:
                parent.child(item_row, 1).setCheckState(Qt.Checked)
            elif self.all_children_excluded(item):
                for child_ix in range(item.rowCount()):
                    item.child(child_ix, 1).setFlags(Qt.ItemIsUserTristate)
            else:
                item.setCheckState(Qt.Checked)
                for child_ix in range(item.rowCount()):
                    item.child(child_ix, 1).setCheckState(Qt.Checked)
                    item.child(child_ix, 1).setFlags(Qt.ItemIsUserTristate)
        elif exclusion_checkstate == Qt.Checked:
            if self.all_children_excluded(parent):
                # make parent partially checked if all children are checked
                if parent != root:
                    grandparent = parent.parent()
                    if grandparent is None:
                        grandparent = root
                    if parent.isEnabled():
                        grandparent.child(parent.row(), 1).setCheckState(Qt.PartiallyChecked)
            item.setCheckState(Qt.Unchecked)
            item.setFlags(Qt.ItemIsUserTristate)
            for child_ix in range(item.rowCount()):
                item.child(child_ix, 1).setCheckState(Qt.Checked)
                item.child(child_ix, 1).setFlags(Qt.ItemIsUserTristate)

    def all_children_excluded(self, parent):
        all_excluded = True
        for child_ix in range(parent.rowCount()):
            if parent.child(child_ix, 1).checkState() != Qt.Checked and parent.child(child_ix, 1).isEnabled():
                all_excluded = False
                break
        return all_excluded

    def build_tree_structure_threaded(self, root_path):
        worker = Worker(record_stat, root_path)
        worker.signals.started.connect(self.build_tree_started)
        worker.signals.result.connect(self.build_tree_finished)
        self.threadpool.start(worker)

    def build_tree_started(self):
        """ Status messages when building a tree should be placed here. """
        self.expanded_items_list = []
        self.unchecked_items_set = set()
        self.spinner.start()

    def build_tree_finished(self, result):
        """ Status messages when tree building is complete should be
        placed here. """
        self.og_dir_dict = result
        self.og_dir_dict = compute_stat(self.og_dir_dict)
        self.refresh_treeview(self.og_model, self.og_tree, self.og_dir_dict)
        self.save_btn.setEnabled(True)
        self.less_btn.setEnabled(True)
        self.spinner.stop()

    def clear_root(self):
        self.root_path = None
        self.og_dir_dict = dict()
        self.unchecked_items_set = set()
        self.og_model.removeRow(0)

    def load_dir_dicts(self, og_dir_dict, anon_dir_dict=None, checkable=True, expand_all=False):
        self.og_dir_dict = _pickle.loads(_pickle.dumps(og_dir_dict))
        if anon_dir_dict is not None:
            self.anon_dir_dict = _pickle.loads(_pickle.dumps(anon_dir_dict))
        else:
            self.anon_dir_dict = _pickle.loads(_pickle.dumps(self.og_dir_dict))
        self.refresh_treeview(self.og_model, self.og_tree, self.og_dir_dict, checkable=checkable, expand_all=expand_all)

    def save_checkstates(self, dir_dict, item):
        parent = item.parent()
        if parent is None:
            parent = self.og_model.invisibleRootItem()
        dirkey = item.data(Qt.UserRole)
        row = item.row()
        dir_dict[dirkey]['selection_state'] = parent.child(row, 0).checkState()
        dir_dict[dirkey]['exclusion_state'] = parent.child(row, 1).checkState()
        for child_ix in range(item.rowCount()):
            self.save_checkstates(dir_dict, item.child(child_ix))

    def save_checkstates_root(self, dir_dict):
        root = self.og_model.invisibleRootItem()
        for child_ix in range(root.rowCount()):
            self.save_checkstates(dir_dict, root.child(child_ix))

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


class KeyTreeOperations(TreeOperations):
    def __init__(self, og_tree, threadpool, spinner,
                 select_btn=None, save_btn=None, load_btn=None, less_btn=None):
        # super().__init__(og_tree, threadpool, spinner, select_btn, save_btn, load_btn, less_btn)
        og_model_headers = ['Folder Name', 'Exclude', 'Key']
        self.unchecked_items_set = set()
        self.expanded_items_list = []
        self.threadpool = threadpool
        self.spinner = spinner
        self.root_path = Path('~').expanduser()
        self.select_btn = select_btn
        self.save_btn = save_btn
        self.load_btn = load_btn
        self.less_btn = less_btn

        # Initialize model and tree
        self.og_tree = og_tree
        self.og_dir_dict, self.anon_dir_dict = dict(), dict()
        self.og_model = QStandardItemModel()
        self.og_tree.setModel(self.og_model)
        self.og_model.setHorizontalHeaderLabels(og_model_headers)
        self.refresh_treeview(self.og_model, self.og_tree, self.og_dir_dict)
        self.og_tree.setItemsExpandable(False)

    def append_all_children(self, dirkey, dir_dict, parent_item,
                            checkable=True, anon_tree=False):
        if dirkey in dir_dict:
            dirname = QStandardItem(dir_dict[dirkey]['dirname'])
            exclusion = QStandardItem('')
            description = QStandardItem(dir_dict[dirkey]['description'])
            items = [dirname, exclusion, description]
            dirname.setData(dirkey, Qt.UserRole)
            if checkable is True:
                dirname.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
                    Qt.ItemIsUserCheckable)
                exclusion.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate |
                    Qt.ItemIsUserCheckable)
            elif checkable is False:
                dirname.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate)
                exclusion.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsUserTristate)
            selection_state = dir_dict[dirkey]['selection_state']
            exclusion_state = dir_dict[dirkey]['exclusion_state']
            if selection_state is not None:
                dirname.setCheckState(selection_state)
            else:
                dirname.setCheckState(Qt.Unchecked)
            if exclusion_state is not None:
                exclusion.setCheckState(exclusion_state)
            else:
                exclusion.setCheckState(Qt.Unchecked)
            parent_item.appendRow(items)
            child_ix = parent_item.rowCount() - 1
            parent_item = parent_item.child(child_ix)
            children_keys = dir_dict[dirkey]['childkeys']
            for child_key in sorted(children_keys):
                self.append_all_children(child_key, dir_dict, parent_item,
                                         checkable, anon_tree)


# the whole app
if __name__ == '__main__':
    import sys
    app = QApplication([])
    main = Main()
    main.show()
    sys.exit(app.exec_())

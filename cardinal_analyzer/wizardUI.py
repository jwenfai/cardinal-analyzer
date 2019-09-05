from PyQt5 import QtCore, QtGui, QtWidgets


class WizardUI(object):
    def setup_ui(self, wizard):
        wizard.setObjectName("wizard")
        wizard.resize(732, 425)
        wizard.setMinimumSize(QtCore.QSize(575, 400))
        wizard.setWindowTitle("Cardinal-Analyzer")
        wizard.setOptions(QtWidgets.QWizard.NoBackButtonOnStartPage | QtWidgets.QWizard.NoCancelButton)
        wizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)

        # page 1 contents
        self.wizardpage1 = QtWidgets.QWizardPage()
        self.wizardpage1.setObjectName("wizardpage1")
        self.gridlayout_wp1_0 = QtWidgets.QGridLayout(self.wizardpage1)
        self.gridlayout_wp1_0.setObjectName("gridlayout_wp1")

        self.scrollarea = QtWidgets.QScrollArea(self.wizardpage1)
        self.scrollarea.setMinimumSize(QtCore.QSize(400, 0))
        self.scrollarea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setObjectName("scrollarea")
        self.scrollarea_widget = QtWidgets.QWidget()
        self.scrollarea_widget.setGeometry(QtCore.QRect(0, 0, 684, 374))
        self.scrollarea_widget.setObjectName("scrollarea_widget")
        self.gridlayout_wp1_1 = QtWidgets.QGridLayout(self.scrollarea_widget)
        self.gridlayout_wp1_1.setObjectName("gridlayout")
        self.verticallayout_wp1_0 = QtWidgets.QVBoxLayout()
        self.verticallayout_wp1_0.setObjectName("verticallayout")

        self.consentbox = QtWidgets.QCheckBox(self.scrollarea_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.consentbox.sizePolicy().hasHeightForWidth())
        self.consentbox.setSizePolicy(sizePolicy)
        self.consentbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.consentbox.setObjectName("consentbox")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.welcomelabel = QtWidgets.QLabel(self.scrollarea_widget)
        self.welcomelabel.setFont(font)
        self.welcomelabel.setWordWrap(True)
        self.welcomelabel.setOpenExternalLinks(True)
        self.welcomelabel.setObjectName("welcomelabel")
        self.reblabel = QtWidgets.QLabel(self.scrollarea_widget)
        self.reblabel.setFont(font)
        self.reblabel.setWordWrap(True)
        self.reblabel.setOpenExternalLinks(True)
        self.reblabel.setObjectName("reblabel")
        self.consent_savebutton = QtWidgets.QPushButton(self.scrollarea_widget)
        self.consent_savebutton.setObjectName("consent_savebutton")

        self.verticallayout_wp1_0.addWidget(self.welcomelabel)
        self.verticallayout_wp1_0.addWidget(self.consentbox)
        self.verticallayout_wp1_0.addWidget(self.reblabel)
        self.verticallayout_wp1_0.addWidget(
            self.consent_savebutton, 0, QtCore.Qt.AlignHCenter)
        self.gridlayout_wp1_1.addLayout(self.verticallayout_wp1_0, 1, 0, 1, 1)
        self.scrollarea.setWidget(self.scrollarea_widget)
        self.gridlayout_wp1_0.addWidget(self.scrollarea, 0, 0, 1, 1)

        # page 2 contents
        self.wizardpage2 = QtWidgets.QWizardPage()
        self.wizardpage2.setObjectName("wizardpage2")
        self.verticallayout_wp2_0 = QtWidgets.QVBoxLayout(self.wizardpage2)
        self.verticallayout_wp2_0.setObjectName("verticallayout_wp2_0")
        self.horizontallayout_wp2_0 = QtWidgets.QHBoxLayout()
        self.horizontallayout_wp2_0.setObjectName("horizontallayout_wp2_0")

        self.og_tree_0 = QtWidgets.QTreeView()
        # self.select_btn_0 = QtWidgets.QPushButton()
        # self.select_btn_0.resize(self.select_btn_0.sizeHint())
        # self.save_btn_0 = QtWidgets.QPushButton()
        # self.save_btn_0.resize(self.save_btn_0.sizeHint())
        # self.save_btn_0.setDisabled(True)
        # self.load_btn_0 = QtWidgets.QPushButton()
        # self.load_btn_0.resize(self.save_btn_0.sizeHint())
        self.reset_demo_btn = QtWidgets.QPushButton()
        self.reset_demo_btn.resize(self.reset_demo_btn.sizeHint())
        self.horizontallayout_wp2_0.addStretch(1)
        # self.horizontallayout_wp2_0.addWidget(self.select_btn_0)
        # self.horizontallayout_wp2_0.addWidget(self.save_btn_0)
        # self.horizontallayout_wp2_0.addWidget(self.load_btn_0)
        self.horizontallayout_wp2_0.addWidget(self.reset_demo_btn)
        self.horizontallayout_wp2_0.addStretch(1)
        self.verticallayout_wp2_0.addWidget(self.og_tree_0)
        self.verticallayout_wp2_0.addLayout(self.horizontallayout_wp2_0)

        # page 3 contents
        self.wizardpage3 = QtWidgets.QWizardPage()
        self.wizardpage3.setObjectName("wizardpage3")
        self.verticallayout_wp3_0 = QtWidgets.QVBoxLayout(self.wizardpage3)
        self.verticallayout_wp3_0.setObjectName("verticallayout_wp3_0")
        self.horizontallayout_wp3_0 = QtWidgets.QHBoxLayout()
        self.horizontallayout_wp3_0.setObjectName("horizontallayout_wp3_0")

        self.textarea_wp3_0 = QtWidgets.QPlainTextEdit()
        # self.software_savebutton = QtWidgets.QPushButton()
        # self.software_savebutton.resize(self.software_savebutton.sizeHint())
        # self.horizontallayout_wp3_0.addStretch(1)
        # self.horizontallayout_wp3_0.addWidget(self.software_savebutton)
        # self.horizontallayout_wp3_0.addStretch(1)
        self.verticallayout_wp3_0.addWidget(self.textarea_wp3_0)
        self.verticallayout_wp3_0.addLayout(self.horizontallayout_wp3_0)

        # page 4 contents
        self.wizardpage4 = QtWidgets.QWizardPage()
        self.wizardpage4.setObjectName("wizardpage4")
        self.verticallayout_wp4_0 = QtWidgets.QVBoxLayout(self.wizardpage4)
        self.verticallayout_wp4_0.setObjectName("verticallayout_wp4_0")
        self.horizontallayout_wp4_0 = QtWidgets.QHBoxLayout()
        self.horizontallayout_wp4_0.setObjectName("horizontallayout_wp4_0")

        self.og_tree_1 = QtWidgets.QTreeView()
        self.select_btn_1 = QtWidgets.QPushButton()
        self.select_btn_1.resize(self.select_btn_1.sizeHint())
        self.save_btn_1 = QtWidgets.QPushButton()
        self.save_btn_1.resize(self.save_btn_1.sizeHint())
        self.save_btn_1.setDisabled(True)
        self.load_btn_1 = QtWidgets.QPushButton()
        self.load_btn_1.resize(self.save_btn_1.sizeHint())
        self.horizontallayout_wp4_0.addStretch(1)
        self.horizontallayout_wp4_0.addWidget(self.select_btn_1)
        self.horizontallayout_wp4_0.addWidget(self.save_btn_1)
        self.horizontallayout_wp4_0.addWidget(self.load_btn_1)
        self.horizontallayout_wp4_0.addStretch(1)
        self.verticallayout_wp4_0.addWidget(self.og_tree_1)
        self.verticallayout_wp4_0.addLayout(self.horizontallayout_wp4_0)

        # page 5 contents
        self.wizardpage5 = QtWidgets.QWizardPage()
        self.wizardpage5.setObjectName("wizardpage5")
        self.gridlayout_wp5_0 = QtWidgets.QGridLayout(self.wizardpage4)
        self.gridlayout_wp5_0.setObjectName("gridlayout_wp5")

        # all pages
        self.retranslate_ui(wizard)
        wizard.addPage(self.wizardpage1)
        wizard.addPage(self.wizardpage2)
        wizard.addPage(self.wizardpage3)
        wizard.addPage(self.wizardpage4)
        wizard.addPage(self.wizardpage5)

    def retranslate_ui(self, wizard):
        _translate = QtCore.QCoreApplication.translate
        # page 1 labels
        self.wizardpage1.setTitle(_translate("Wizard", "Introduction"))
        self.wizardpage1.setSubTitle(_translate(
            "Wizard",
            "Read the information below, click the check box if you "
            "understand and consent to participate, and click \'Next\' "
            "to begin."))
        self.welcomelabel.setText(_translate(
            "Wizard",
            "<html><head/><body><p align=\"justify\"><span style=\" "
            "font-weight:600;\">WARNING</span></p><p align=\"justify\">"
            "DEBUG BUILD ONLY. SHOULD  NOT BE RUN BY END USER. Lorem ipsum "
            "-- populate with consent form, contact information, research "
            "ethics approval, etc. <span style=\" font-weight:600;\">"
            "...text...</span><span style=\" font-weight:600; "
            "font-style:italic;\">.</span> ...text... <span style=\" "
            "font-style:italic;\">...text...</span>.</p></body></html>"))
        self.consentbox.setText(_translate(
            "Wizard", "I understand and consent to participate: "))
        self.reblabel.setText(_translate(
            "Wizard",
            "<html><head/><body><p align=\"justify\">This study is conducted "
            "by <a href=\"mailto:jesse.dinneen@mail.mcgill.ca\"><span style=\" "
            "text-decoration: underline; color:#2980b9;\">Jesse David "
            "Dinneen</span></a>, a PhD candidate supervised by Prof. "
            "<a href=\"mailto:charles.julien@mcgill.ca\"><span style=\" "
            "text-decoration: underline; color:#2980b9;\">Charles-Antoine "
            "Julien</span></a> in the School of Information Studies at McGill "
            "University, and is approved by McGill University Research Ethics "
            "Board (#75-0715, \'Understanding file management behavior\'). If "
            "you have any questions or concerns regarding your rights or "
            "welfare as a participant in this research study, please contact "
            "the McGill Ethics Manager at 514-398-6831 or "
            "<a href=\"mailto:lynda.mcneil@mcgill.ca\"><span style=\" "
            "text-decoration: underline; color:#2980b9;\">"
            "lynda.mcneil@mcgill.ca</span></a></p></body></html>"))
        self.consent_savebutton.setText(_translate(
            "Wizard", "Save this info to file (optional)"))
        # page 2 labels
        self.wizardpage2.setTitle(_translate("Wizard", "Familiarization"))
        self.wizardpage2.setSubTitle(_translate(
            "Wizard",
            "a training page that shows some instructions (e.g., a label; "
            "i'll provide text later) above a tree widget like in (3.) but "
            "populated with just a few fake folders (e.g., named Folder 1-4) "
            "so users can try out and learn the functionality"))
        # self.select_btn_0.setText(_translate("Wizard", "Select Root"))
        # self.select_btn_0.setToolTip(_translate(
        #     "Wizard", "Select <b>personal folder</b> for data collection."))
        # self.save_btn_0.setText(_translate("Wizard", "Save Data"))
        # self.save_btn_0.setToolTip(_translate(
        #     "Wizard", "Save data locally as a JSON file."))
        # self.load_btn_0.setText(_translate("Wizard", "Load Data"))
        # self.load_btn_0.setToolTip(_translate(
        #     "Wizard", "Load folder structure from local JSON file."))
        self.reset_demo_btn.setText(_translate("Wizard", "Reset Demo"))
        self.reset_demo_btn.setToolTip(_translate(
            "Wizard", "Return example folder structure to initial state."))

        # page 3 labels
        self.wizardpage3.setTitle(_translate("Wizard", "Software"))
        self.wizardpage3.setSubTitle(_translate(
            "Wizard",
            "Names of any special software you use to access your files"))
        # self.software_savebutton.setText(_translate("Wizard", "Save Info"))
        # self.software_savebutton.setToolTip(_translate(
        #     "Wizard", "Save names of special software used to access files."))

        # page 4 labels
        self.wizardpage4.setTitle(_translate("Wizard", "Analysis"))
        self.wizardpage4.setSubTitle(_translate(
            "Wizard",
            "(A) a small text label with some brief instructions I will "
            "provide later"))
        self.select_btn_1.setText(_translate("Wizard", "Select Root"))
        self.select_btn_1.setToolTip(_translate(
            "Wizard", "Select <b>personal folder</b> for data collection."))
        self.save_btn_1.setText(_translate("Wizard", "Save Data"))
        self.save_btn_1.setToolTip(_translate(
            "Wizard",
            "Save folder structure data and software choices locally as a "
            "JSON file."))
        self.load_btn_1.setText(_translate("Wizard", "Load Data"))
        self.load_btn_1.setToolTip(_translate(
            "Wizard",
            "Load folder structure data and software choices from a "
            "JSON file."))
        # page 5 labels
        self.wizardpage5.setTitle(_translate("Wizard", "Finished!"))
        self.wizardpage5.setSubTitle(_translate(
            "Wizard",
            "Thank you for participating. Click \'Finish\' to exit."))

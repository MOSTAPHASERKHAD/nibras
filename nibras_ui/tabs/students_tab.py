from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
    QFrame, QSplitter, QListWidget, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QDateEdit,
    QFileDialog, QStyledItemDelegate, QStyle, QProgressDialog,
    QInputDialog, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate, QSize, QRect
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QFont
import qtawesome as qta
import pandas as pd
import os
import json
from nibras_core.utils.validators import (
    validate_student_name, validate_date, validate_phone, validate_email
)

class StudentDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor("#3498db"))
            painter.setPen(Qt.white)
        else:
            painter.setPen(Qt.black)

        student_data = index.data(Qt.UserRole)
        if not student_data:
            super().paint(painter, option, index)
            return

        name = student_data.get('name', 'Unknown')
        sid = student_data.get('id', '')
        
        rect = option.rect
        painter.save()
        
        # Draw Icon
        icon_rect = QRect(rect.left() + 10, rect.top() + 10, 40, 40)
        # Placeholder for icon drawing if needed, or just text
        
        # Draw Name
        name_rect = QRect(rect.left() + 60, rect.top() + 5, rect.width() - 70, 25)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, name)
        
        # Draw ID
        id_rect = QRect(rect.left() + 60, rect.top() + 30, rect.width() - 70, 20)
        font.setBold(False)
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(id_rect, Qt.AlignLeft | Qt.AlignVCenter, f"ID: {sid}")
        
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 60)

class StudentsTab(QWidget):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.main_window = parent
        self.student_delegate = StudentDelegate()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Class selection
        class_layout = QHBoxLayout()
        self.class_selector = QComboBox()
        self.class_selector.currentTextChanged.connect(self.on_class_changed)
        
        btn_add_class = self._create_button('fa5s.plus', "إضافة قسم جديد", self.add_new_class)
        btn_delete_class = self._create_button('fa5s.trash', "حذف القسم الحالي", self.delete_current_class, '#e74c3c')
        
        class_layout.addWidget(QLabel("القسم:", styleSheet="font-weight:bold;"))
        class_layout.addWidget(self.class_selector, 1)
        class_layout.addWidget(btn_add_class)
        class_layout.addWidget(btn_delete_class)
        
        # Term selection
        term_layout = QHBoxLayout()
        self.term_selector = QComboBox()
        terms = self.data_manager.get_setting('Teacher', 'terms', fallback='الفصل الأول,الفصل الثاني,الفصل الثالث').split(',')
        self.term_selector.addItems([t.strip() for t in terms])
        
        # Set active term
        active_term = self.data_manager.get_setting('Teacher', 'active_term', fallback=terms[0].strip())
        self.term_selector.setCurrentText(active_term)
        self.term_selector.currentTextChanged.connect(self.on_term_changed)
        
        term_layout.addWidget(QLabel("الفصل الدراسي:", styleSheet="font-weight:bold;"))
        term_layout.addWidget(self.term_selector, 1)
        
        layout.addLayout(class_layout)
        layout.addLayout(term_layout)
        
        # Title and Actions
        title_layout = QHBoxLayout()
        title = QLabel("قائمة التلاميذ")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title)
        
        buttons_vbox = QVBoxLayout()
        buttons_vbox.setSpacing(5)
        btn_add = self._create_button('fa5s.user-plus', "إضافة تلميذ", self.add_student)
        btn_edit = self._create_button('fa5s.user-edit', "تعديل بيانات", self.edit_student)
        btn_delete = self._create_button('fa5s.user-minus', "حذف تلميذ", self.delete_student, '#e74c3c')
        buttons_vbox.addWidget(btn_add)
        buttons_vbox.addWidget(btn_edit)
        buttons_vbox.addWidget(btn_delete)
        buttons_vbox.addStretch()
        
        # Student List
        student_list_layout = QHBoxLayout()
        student_list_layout.addLayout(buttons_vbox)
        
        self.student_list_widget = QListWidget()
        self.student_list_widget.setItemDelegate(self.student_delegate)
        self.student_list_widget.currentItemChanged.connect(self.on_student_selected)
        
        student_list_layout.addWidget(self.student_list_widget, 1)
        
        # Search and Import/Export
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("ابحث عن تلميذ...")
        self.search_bar.textChanged.connect(self.filter_students)
        
        btns_layout = QHBoxLayout()
        btn_import = self._create_button(text=" استيراد", icon_name='fa5s.file-import', callback=self.import_students)
        btn_export_excel = self._create_button(text=" تصدير", icon_name='fa5s.file-excel', callback=self.export_class_to_excel)
        btns_layout.addWidget(btn_import)
        btns_layout.addWidget(btn_export_excel)
        
        layout.addLayout(title_layout)
        layout.addWidget(self.search_bar)
        layout.addLayout(student_list_layout, 1)
        layout.addLayout(btns_layout)
        
        # Load initial data
        self.refresh_class_list()
        
    def _create_button(self, icon_name, tooltip=None, callback=None, color=None, text=None):
        btn = QPushButton(text if text else "")
        if icon_name:
            btn.setIcon(qta.icon(icon_name, color=color if color else 'black'))
        if tooltip:
            btn.setToolTip(tooltip)
        if callback:
            btn.clicked.connect(callback)
        return btn
        
    def refresh_class_list(self):
        self.class_selector.blockSignals(True)
        self.class_selector.clear()
        classes = self.data_manager.get_class_list()
        self.class_selector.addItems(classes)
        
        current = self.data_manager.get_current_class_name()
        if current and current in classes:
            self.class_selector.setCurrentText(current)
            
        self.class_selector.blockSignals(False)
        self.refresh_student_list()
        
    def on_class_changed(self, class_name):
        """معالج تغيير القسم - تحديث جميع التبويبات"""
        if class_name:
            # تحميل القسم الجديد
            self.data_manager.load_class(class_name)
            
            # تحديث قائمة الطلاب في هذا التبويب
            self.refresh_student_list()
            
            # ✅ تحديث التبويبات الأخرى
            if self.main_window:
                # تحديث تبويب الحضور
                if hasattr(self.main_window, 'attendance_tab') and hasattr(self.main_window.attendance_tab, 'load_attendance'):
                    self.main_window.attendance_tab.load_attendance()
                
                # تحديث تبويب السلوك
                if hasattr(self.main_window, 'behavior_tab') and hasattr(self.main_window.behavior_tab, '_refresh_behavior_log'):
                    self.main_window.behavior_tab._refresh_behavior_log()
                
                # تحديث تبويب النتائج الأكاديمية (إذا وُجد)
                if hasattr(self.main_window, 'academic_tab') and hasattr(self.main_window.academic_tab, 'refresh'):
                    try:
                        self.main_window.academic_tab.refresh()
                    except:
                        pass  # قد لا تحتوي على دالة refresh
            
    def on_term_changed(self, term):
        """معالج تغيير الفصل الدراسي"""
        self.data_manager.set_setting('Teacher', 'active_term', term)
        
    def refresh_student_list(self):
        self.student_list_widget.clear()
        students = self.data_manager.get_student_list()
        for s in students:
            from PyQt5.QtWidgets import QListWidgetItem
            item = QListWidgetItem()
            item.setData(Qt.UserRole, s)
            item.setText(f"{s['name']}") # Fallback text
            self.student_list_widget.addItem(item)
            
    def filter_students(self, text):
        for i in range(self.student_list_widget.count()):
            item = self.student_list_widget.item(i)
            data = item.data(Qt.UserRole)
            name = data.get('name', '').lower()
            item.setHidden(text.lower() not in name)
            
    def on_student_selected(self, current, previous):
        """معالج اختيار تلميذ - إشعار النافذة الرئيسية"""
        if not current:
            return
        
        student_data = current.data(Qt.UserRole)
        
        # إذا كانت النافذة الرئيسية تحتوي على دالة لتحديث التفاصيل
        if hasattr(self.main_window, 'on_student_selection_changed'):
            self.main_window.on_student_selection_changed(student_data)
        
        # تحديث التبويبات الأخرى إذا لزم الأمر
        # مثلاً: تحديث تبويب السلوك أو الحضور
        if hasattr(self.main_window, 'behavior_tab'):
            # يمكن إضافة منطق التحديث هنا
            pass
        
    def add_student(self):
        # Simplified dialog for adding student
        dialog = QDialog(self)
        dialog.setWindowTitle("إضافة تلميذ جديد")
        layout = QFormLayout(dialog)
        
        first_name = QLineEdit()
        last_name = QLineEdit()
        dob = QDateEdit(QDate.currentDate())
        dob.setDisplayFormat("yyyy-MM-dd")
        
        layout.addRow("اللقب:", last_name)
        layout.addRow("الاسم:", first_name)
        layout.addRow("تاريخ الميلاد:", dob)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            data = {
                'first_name': first_name.text(),
                'last_name': last_name.text(),
                'dob': dob.date().toString("yyyy-MM-dd")
            }
            self.data_manager.add_or_update_student(data)
            self.refresh_student_list()
            
    def edit_student(self):
        current = self.student_list_widget.currentItem()
        if not current:
            return
            
        data = current.data(Qt.UserRole)
        sid = data['id']
        student_data = self.data_manager.get_student_data(sid)
        details = student_data.get('details', {})
        
        dialog = QDialog(self)
        dialog.setWindowTitle("تعديل بيانات تلميذ")
        layout = QFormLayout(dialog)
        
        first_name = QLineEdit(details.get('first_name', ''))
        last_name = QLineEdit(details.get('last_name', ''))
        dob_str = details.get('dob', '')
        dob = QDateEdit()
        if dob_str:
            dob.setDate(QDate.fromString(dob_str, "yyyy-MM-dd"))
        else:
            dob.setDate(QDate.currentDate())
        dob.setDisplayFormat("yyyy-MM-dd")
        
        layout.addRow("اللقب:", last_name)
        layout.addRow("الاسم:", first_name)
        layout.addRow("تاريخ الميلاد:", dob)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            new_data = details.copy()
            new_data.update({
                'first_name': first_name.text(),
                'last_name': last_name.text(),
                'dob': dob.date().toString("yyyy-MM-dd")
            })
            self.data_manager.add_or_update_student(new_data, sid)
            self.refresh_student_list()

    def delete_student(self):
        current = self.student_list_widget.currentItem()
        if not current:
            return
            
        data = current.data(Qt.UserRole)
        sid = data['id']
        name = data['name']
        
        reply = QMessageBox.question(self, "تأكيد الحذف", f"هل أنت متأكد من حذف التلميذ {name}؟",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_student(sid)
            self.refresh_student_list()
            
    def add_new_class(self):
        name, ok = QInputDialog.getText(self, "إضافة قسم", "اسم القسم الجديد:")
        if ok and name:
            if self.data_manager.create_class(name):
                self.refresh_class_list()
            else:
                QMessageBox.warning(self, "خطأ", "القسم موجود بالفعل")

    def delete_current_class(self):
        current = self.class_selector.currentText()
        if not current:
            return
            
        reply = QMessageBox.question(self, "تأكيد الحذف", f"هل أنت متأكد من حذف القسم {current}؟",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_class(current)
            self.refresh_class_list()

    def import_students(self):
        filename, _ = QFileDialog.getOpenFileName(self, "استيراد تلاميذ", "", "Excel Files (*.xlsx *.xls)")
        if not filename:
            return

        try:
            df = pd.read_excel(filename)
            required_columns = ['اللقب', 'الاسم', 'تاريخ الميلاد']
            if not all(col in df.columns for col in required_columns):
                QMessageBox.warning(self, "خطأ", "الملف يجب أن يحتوي على الأعمدة: اللقب، الاسم، تاريخ الميلاد")
                return

            count = 0
            for _, row in df.iterrows():
                dob = row['تاريخ الميلاد']
                # Handle date formats
                if isinstance(dob, pd.Timestamp):
                    dob = dob.strftime('%Y-%m-%d')
                else:
                    dob = str(dob)

                details = {
                    'first_name': str(row['الاسم']),
                    'last_name': str(row['اللقب']),
                    'dob': dob,
                    'pob': str(row.get('مكان الميلاد', '')),
                    'gender': str(row.get('الجنس', '')),
                    'father_name': str(row.get('اسم الأب', '')),
                    'father_job': str(row.get('مهنة الأب', '')),
                    'mother_name': str(row.get('اسم الأم', '')),
                    'mother_job': str(row.get('مهنة الأم', '')),
                    'phone': str(row.get('الهاتف', '')),
                    'health_notes': str(row.get('ملاحظات صحية', '')),
                    'notes': str(row.get('ملاحظات عامة', ''))
                }
                
                # Basic validation
                if details['first_name'] and details['last_name']:
                    self.data_manager.add_or_update_student(details)
                    count += 1

            self.refresh_student_list()
            QMessageBox.information(self, "نجاح", f"تم استيراد {count} تلميذ بنجاح.")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الاستيراد: {str(e)}")

    def export_class_to_excel(self):
        current_class = self.data_manager.get_current_class_name()
        if not current_class:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار قسم أولاً.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "تصدير إلى Excel", f"{current_class}.xlsx", "Excel Files (*.xlsx)")
        if not filename:
            return

        try:
            progress = QProgressDialog("جاري تصدير البيانات...", "إلغاء", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(10)
            
            students = self.data_manager.get_student_list()
            if not students:
                QMessageBox.warning(self, "تنبيه", "لا يوجد تلاميذ لتصديرهم.")
                return
                
            progress.setValue(30)
            
            data = []
            total_students = len(students)
            
            for i, s in enumerate(students):
                if progress.wasCanceled():
                    return
                    
                s_data = self.data_manager.get_student_data(s['id'])
                details = s_data.get('details', {})
                
                row = {
                    'اللقب': details.get('last_name', ''),
                    'الاسم': details.get('first_name', ''),
                    'تاريخ الميلاد': details.get('dob', ''),
                    'مكان الميلاد': details.get('pob', ''),
                    'الجنس': details.get('gender', ''),
                    'اسم الأب': details.get('father_name', ''),
                    'مهنة الأب': details.get('father_job', ''),
                    'اسم الأم': details.get('mother_name', ''),
                    'مهنة الأم': details.get('mother_job', ''),
                    'الهاتف': details.get('phone', ''),
                    'ملاحظات صحية': details.get('health_notes', ''),
                    'ملاحظات عامة': details.get('notes', '')
                }
                data.append(row)
                
                current_progress = 30 + int((i / total_students) * 50)
                progress.setValue(current_progress)

            progress.setValue(85)
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            progress.setValue(100)
            QMessageBox.information(self, "نجاح", "تم تصدير البيانات بنجاح.")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التصدير: {str(e)}")

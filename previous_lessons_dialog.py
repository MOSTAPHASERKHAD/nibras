from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QTextBrowser, QLabel, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import qtawesome as qta
from nibras_core.managers.localization_manager import localization

class PreviousLessonsDialog(QDialog):
    data_changed = pyqtSignal()
    lesson_selected_for_edit = pyqtSignal(str)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.lessons = {}

        self.setWindowTitle(localization.get('prev_lessons_title'))
        self.setMinimumSize(800, 600)

        self.layout = QHBoxLayout(self)

        # Left Panel: Lessons List
        left_panel = QVBoxLayout()
        info_label = QLabel(localization.get('prev_lessons_select_hint'))
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        left_panel.addWidget(info_label)

        self.lessons_list = QListWidget()
        self.lessons_list.currentItemChanged.connect(self.display_lesson_details)
        self._populate_lessons_list()
        btn_load_edit = QPushButton(localization.get('prev_lessons_load_btn'))
        btn_load_edit.setIcon(qta.icon('fa5s.edit', color='white'))
        btn_load_edit.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px; "
            "font-size: 12pt; font-weight: bold; border-radius: 5px;"
        )
        btn_load_edit.clicked.connect(self.load_for_editing)

        btn_delete = QPushButton(localization.get('prev_lessons_delete_btn'))
        btn_delete.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        btn_delete.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px; "
            "font-size: 12pt; font-weight: bold; border-radius: 5px;"
        )
        btn_delete.clicked.connect(self.delete_selected_lesson)

        left_panel.addWidget(self.lessons_list)
        left_panel.addWidget(btn_load_edit)
        left_panel.addWidget(btn_delete)

        # Right Panel: Lesson Details
        right_panel = QVBoxLayout()
        self.details_browser = QTextBrowser()
        self.details_browser.setFont(QFont("Segoe UI", 14, QFont.Bold))
        right_panel.addWidget(QLabel(f"<b style='font-size: 14pt;'>{localization.get('prev_lessons_details_title')}</b>"))
        right_panel.addWidget(self.details_browser)

        self.layout.addLayout(left_panel, 1)
        self.layout.addLayout(right_panel, 2)

        if self.lessons_list.count() > 1: # more than just the "no lessons" message
            self.lessons_list.setCurrentRow(1) # Select first actual lesson
        else:
            self.details_browser.setText(
                "<p style='text-align: center; color: #95a5a6; font-size: 14pt;'>"
                f"{localization.get('prev_lessons_no_lessons_msg')}"
                "</p>"
            )

    def _populate_lessons_list(self):
        self.lessons_list.clear()
        self.lessons.clear()
        
        try:
            # محاولة تحديث البيانات من المصدر لضمان ظهور الدروس الجديدة
            # نستخدم مدير الأقسام لإعادة تحميل البيانات بشكل صحيح
            current_class = self.data_manager.get_current_class_name()
            if hasattr(self.data_manager, 'class_manager'):
                self.data_manager.class_manager.load_class(current_class)
            
            # Force cache clear to get fresh metadata
            if hasattr(self.data_manager, '_clear_data_cache'):
                self.data_manager._clear_data_cache()
        except Exception as e:
            print(f"Warning: Could not refresh class data: {e}")

        # قراءة البيانات (سواء تم التحديث أم لا)
        all_lessons_by_date = self.data_manager.get_class_metadata().get("daily_lesson_plan", {})
        
        if not all_lessons_by_date:
            self.lessons_list.addItem(localization.get('prev_lessons_no_lessons_list'))
        else:
            for date_str, lessons_on_day in sorted(all_lessons_by_date.items(), reverse=True):
                date_item = QListWidgetItem(f"--- {date_str} ---")
                date_item.setFlags(Qt.NoItemFlags)
                date_item.setForeground(QColor("#3498db"))
                self.lessons_list.addItem(date_item)
                for lesson_id, lesson_details in lessons_on_day.items():
                    lesson_item = QListWidgetItem(lesson_id)
                    lesson_item.setData(Qt.UserRole + 1, date_str)
                    self.lessons_list.addItem(lesson_item)
                    self.lessons[lesson_id] = lesson_details

    def display_lesson_details(self, current_item, previous_item):
        if not current_item or not current_item.flags() & Qt.ItemIsSelectable:
            self.details_browser.clear()
            return

        lesson_id = current_item.text()
        date_str = current_item.data(Qt.UserRole + 1)

        lesson_id = current_item.text()
        date_str = current_item.data(Qt.UserRole + 1)

        html = f"<h3>{localization.get('prev_lessons_lesson_evals').format(lesson=lesson_id)}</h3><hr>"
        html += f"<p><b>{localization.get('prev_lessons_date')}</b> {date_str}</p>"
        html += "<table width='100%' border='1' style='border-collapse: collapse;' cellpadding='5'>"
        html += f"<tr style='background-color: #f0f0f0;'><th>{localization.get('prev_lessons_header_student')}</th><th>{localization.get('prev_lessons_header_eval')}</th></tr>"

        any_evaluations = False
        for sid in self.data_manager.get_student_list():
            s_data = self.data_manager.get_student_data(sid)
            name = f"{s_data.get('details', {}).get('last_name', '')} {s_data.get('details', {}).get('first_name', '')}"
            
            # البحث عن التقييمات في الهيكل الجديد (تحت الفصول) والقديم
            eval_root = s_data.get("evaluation", {})
            eval_data = {}
            
            # 1. البحث في الهيكل القديم (مباشرة تحت التاريخ)
            if date_str in eval_root and lesson_id in eval_root[date_str]:
                eval_data = eval_root[date_str][lesson_id]
            
            # 2. البحث في الهيكل الجديد (تحت الفصول)
            if not eval_data:
                for term_key, term_data in eval_root.items():
                    if isinstance(term_data, dict) and date_str in term_data:
                         if lesson_id in term_data[date_str]:
                             eval_data = term_data[date_str][lesson_id]
                             break
            
            # 3. محاولة المطابقة المرنة (Fuzzy Match) إذا لم نجد تطابق تام
            if not eval_data:
                 normalized_lesson = lesson_id.replace(" ", "")
                 # بحث في كل مكان
                 stack = [eval_root]
                 while stack:
                     current = stack.pop()
                     if isinstance(current, dict):
                         # هل وصلنا لمستوى الدروس؟ (المفاتيح هي معرفات دروس)
                         for k, v in current.items():
                             if isinstance(v, dict):
                                 if k.replace(" ", "") == normalized_lesson:
                                     eval_data = v
                                     break
                                 stack.append(v)
                         if eval_data: break

            if eval_data:
                any_evaluations = True
                eval_text = "<br>".join([f"<b>{k}:</b> {v}" for k, v in eval_data.items()])
            else:
                eval_text = f"<i>{localization.get('prev_lessons_not_evaluated')}</i>"

            html += f"<tr><td><b>{name}</b></td><td>{eval_text}</td></tr>"

        html += "</table>"

        if not any_evaluations:
            html += f"<p style='text-align: center; color: #7f8c8d; padding: 20px;'>{localization.get('prev_lessons_no_evals_recorded')}</p>"

        self.details_browser.setHtml(html)

    def load_for_editing(self):
        current_item = self.lessons_list.currentItem()
        if not current_item or not current_item.flags() & Qt.ItemIsSelectable:
            QMessageBox.warning(self, localization.get('error'), localization.get('prev_lessons_error_select'))
            return

        lesson_id = current_item.text()
        reply = QMessageBox.question(
            self, 
            localization.get('prev_lessons_confirm_load_title'), 
            localization.get('prev_lessons_confirm_load_msg').format(lesson=lesson_id), 
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self.lesson_selected_for_edit.emit(lesson_id)
            self.accept()

    def delete_selected_lesson(self):
        current_item = self.lessons_list.currentItem()
        if not current_item or not current_item.flags() & Qt.ItemIsSelectable:
            return

        lesson_id = current_item.text()
        date_str = current_item.data(Qt.UserRole + 1)
        
        reply = QMessageBox.question(self, localization.get('msg_confirm_delete'),
                                     localization.get('prev_lessons_confirm_delete_msg').format(lesson=lesson_id),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            metadata = self.data_manager.get_class_metadata()

            # حذف الدرس من الميتاداتا
            if date_str in metadata.get("daily_lesson_plan", {}) and lesson_id in metadata["daily_lesson_plan"][date_str]:
                del metadata["daily_lesson_plan"][date_str][lesson_id]

            # حذف التقويمات والبيانات الأكاديمية من سجلات التلاميذ
            for sid in self.data_manager.get_student_list():
                s_data = self.data_manager.get_student_data(sid)

                # 1. حذف من الهيكل القديم المسطح (للتوافق مع البيانات القديمة)
                if date_str in s_data.get("evaluation", {}) and lesson_id in s_data["evaluation"][date_str]:
                    del s_data["evaluation"][date_str][lesson_id]
                
                # 2. حذف من الهيكل الجديد القائم على الفصول الدراسية
                eval_root = s_data.get("evaluation", {})
                for term_key, term_data in list(eval_root.items()):
                    # التحقق من أن term_data هو قاموس (فصل دراسي) وليس تاريخ مباشر
                    if isinstance(term_data, dict) and date_str in term_data:
                        if isinstance(term_data[date_str], dict) and lesson_id in term_data[date_str]:
                            del term_data[date_str][lesson_id]
                            # إذا أصبح اليوم فارغاً، احذفه أيضاً
                            if not term_data[date_str]:
                                del term_data[date_str]
                
                # 3. حذف البيانات الأكاديمية (من الهيكل القديم)
                for subject in s_data.get("academic", {}):
                    if date_str in s_data["academic"][subject] and lesson_id in s_data["academic"][subject][date_str]:
                        del s_data["academic"][subject][date_str][lesson_id]
                
                # 4. حذف البيانات الأكاديمية من الهيكل الجديد (إن وجد)
                academic_root = s_data.get("academic", {})
                for term_key, term_data in list(academic_root.items()):
                    if isinstance(term_data, dict):
                        for subject, subject_data in list(term_data.items()):
                            if isinstance(subject_data, dict) and date_str in subject_data:
                                if isinstance(subject_data[date_str], dict) and lesson_id in subject_data[date_str]:
                                    del subject_data[date_str][lesson_id]
                                    if not subject_data[date_str]:
                                        del subject_data[date_str]

            self.data_manager.save_class(show_success_message=False)
            QMessageBox.information(self, localization.get('msg_deleted'), localization.get('prev_lessons_delete_success'))
            self.data_changed.emit() # إرسال الإشارة قبل الإغلاق
            self.accept()
# Force recompilation
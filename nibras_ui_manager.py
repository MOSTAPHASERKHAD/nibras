# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qtawesome as qta

class UIManager:
    def __init__(self, app):
        self.app = app

    def _setup_ui(self):
        self.app.setWindowIcon(qta.icon('fa5s.graduation-cap', color='#2c3e50'))
        self.app.update_window_title()
        
        self.create_menu()
        main_widget = QWidget()
        self.app.setCentralWidget(main_widget)
        self.app.main_layout = QHBoxLayout(main_widget)
        self.app.main_layout.setContentsMargins(0, 0, 0, 0)
        self.app.main_layout.setSpacing(0)
        self.create_students_section()
        self.create_main_panel()
        
        self.app.main_layout.addWidget(self.app.students_frame, 1)
        self.app.main_layout.addWidget(self.app.main_panel_frame, 4)

    def create_menu(self):
        self.app.menu_bar = QMenuBar(self.app)
        self.app.setMenuBar(self.app.menu_bar)
        file_menu = self.app.menu_bar.addMenu("ملف")
        
        timetable_action = QAction("إعداد جدول التوقيت", self.app)
        timetable_action.triggered.connect(self.app.open_timetable_dialog)
        settings_action = QAction("الإعدادات العامة", self.app)
        settings_action.triggered.connect(self.app.open_settings)
        change_pass_action = QAction("تغيير كلمة المرور", self.app)
        change_pass_action.triggered.connect(self.app.change_password)
        edit_teacher_info_action = QAction("تعديل معلومات المعلم", self.app)
        edit_teacher_info_action.triggered.connect(self.app.edit_teacher_info)
        edit_criteria_action = QAction("تعديل معايير التقويم", self.app)
        edit_criteria_action.triggered.connect(self.app.edit_evaluation_criteria)
        # edit_subjects_action = QAction("تعديل المواد الأكاديمية", self.app)
        # edit_subjects_action.triggered.connect(self.app.edit_academic_subjects)
        theme_action = QAction("المظهر...", self.app)
        theme_action.triggered.connect(self.app.open_theme_dialog)
        exit_action = QAction("حفظ وخروج", self.app)
        exit_action.triggered.connect(self.app.close)
        
        file_menu.addAction(timetable_action)
        file_menu.addSeparator()
        file_menu.addAction(edit_teacher_info_action)
        file_menu.addAction(edit_criteria_action)
        # file_menu.addAction(edit_subjects_action)
        file_menu.addSeparator()
        file_menu.addAction(theme_action)
        file_menu.addAction(settings_action)
        file_menu.addAction(change_pass_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

    def create_students_section(self):
        self.app.students_frame = QFrame()
        self.app.students_frame.setObjectName("studentsPanel")
        layout = QVBoxLayout(self.app.students_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        class_layout = QHBoxLayout()
        self.app.class_selector = QComboBox()
        btn_add_class = self.app._create_button(icon='fa5s.plus', tip="إضافة قسم جديد", callback=self.app.add_new_class, obj_name="toolButton")
        btn_delete_class = self.app._create_button(icon='fa5s.trash', color='#e74c3c', tip="حذف القسم الحالي", callback=self.app.delete_current_class, obj_name="toolButton")
        class_layout.addWidget(QLabel("القسم:", styleSheet="color:white; font-weight:bold;"))
        class_layout.addWidget(self.app.class_selector, 1)
        class_layout.addWidget(btn_add_class)
        class_layout.addWidget(btn_delete_class)

        title_layout = QHBoxLayout()
        title = QLabel("قائمة التلاميذ")
        title.setObjectName("headerTitle")
        title_layout.addWidget(title)
        
        buttons_vbox = QVBoxLayout()
        buttons_vbox.setSpacing(5)
        btn_add = self.app._create_button(icon='fa5s.user-plus', tip="إضافة تلميذ", callback=self.app.add_student, obj_name="toolButton")
        btn_edit = self.app._create_button(icon='fa5s.user-edit', tip="تعديل بيانات", callback=self.app.edit_student, obj_name="toolButton")
        btn_delete = self.app._create_button(icon='fa5s.user-minus', color='#e74c3c', tip="حذف تلميذ", callback=self.app.delete_student, obj_name="toolButton")
        buttons_vbox.addWidget(btn_add)
        buttons_vbox.addWidget(btn_edit)
        buttons_vbox.addWidget(btn_delete)
        buttons_vbox.addStretch()

        student_list_layout = QHBoxLayout()
        student_list_layout.addLayout(buttons_vbox)
        
        self.app.student_list_widget = QListWidget()
        self.app.student_list_widget.setItemDelegate(self.app.student_delegate)
        
        student_list_layout.addWidget(self.app.student_list_widget, 1)

        self.app.search_bar = QLineEdit()
        self.app.search_bar.setObjectName("searchBar")
        self.app.search_bar.setPlaceholderText("ابحث عن تلميذ...")
        
        btns_layout = QHBoxLayout()
        btn_import = self.app._create_button(text=" استيراد", icon='fa5s.file-import', callback=self.app.import_students)
        btn_export_excel = self.app._create_button(text=" تصدير", icon='fa5s.file-excel', callback=self.app.export_class_to_excel)
        btns_layout.addWidget(btn_import)
        btns_layout.addWidget(btn_export_excel)

        layout.addLayout(class_layout)
        layout.addLayout(title_layout)
        layout.addWidget(self.app.search_bar)
        layout.addLayout(student_list_layout, 1)
        layout.addLayout(btns_layout)

    def create_main_panel(self):
        self.app.main_panel_frame = QFrame()
        self.app.main_panel_frame.setObjectName("mainPanel")
        layout = QVBoxLayout(self.app.main_panel_frame)
        layout.setContentsMargins(10, 5, 10, 10) 
        
        self.app.tabs = QTabWidget()
        self.app.tabs.setTabPosition(QTabWidget.West)

        self.app.tab_daily_management = QWidget()
        self.app.tab_timeline = QWidget()
        self.app.tab_attendance = QWidget()
        self.app.tab_behavior = QWidget()
        self.app.tab_evaluation = QWidget()
        self.app.tab_academic = QWidget()
        self.app.tab_grades = QWidget()
        self.app.tab_tools = QWidget()
        self.app.tab_resources = QWidget()
        self.app.tab_timetable = QWidget()
        
        self.app.tabs.addTab(self.app.tab_daily_management, qta.icon('fa5s.chalkboard-teacher'), "إدارة اليوم")
        self.app.tabs.addTab(self.app.tab_timeline, qta.icon('fa5s.user-clock'), "الملف الشامل")
        self.app.tabs.addTab(self.app.tab_attendance, qta.icon('fa5s.calendar-check'), "الحضــور")
        self.app.tabs.addTab(self.app.tab_behavior, qta.icon('fa5s.star'), "السلوك")
        self.app.tabs.addTab(self.app.tab_evaluation, qta.icon('fa5s.clipboard-check'), "التقويم اليومي")
        self.app.tabs.addTab(self.app.tab_academic, qta.icon('fa5s.book-open'), "المتابعة الأكاديمية")
        self.app.tabs.addTab(self.app.tab_grades, qta.icon('fa5s.chart-bar'), "ملخص الأداء")
        self.app.tabs.addTab(self.app.tab_tools, qta.icon('fa5s.tools'), "أدوات الفصل")
        self.app.tabs.addTab(self.app.tab_resources, qta.icon('fa5s.folder-open'), "الموارد")
        self.app.tabs.addTab(self.app.tab_timetable, qta.icon('fa5s.calendar-alt'), "جدول التوقيت")

        self.create_daily_management_tab()
        self.create_timeline_tab()
        self.create_attendance_tab()
        self.create_behavior_tab()
        self.create_academic_tab()
        self.create_evaluation_tab()
        self.create_grades_tab()
        self.create_tools_tab()
        self.create_resources_tab()
        self.create_interactive_timetable_tab()

        layout.addWidget(self.app.tabs, 1)
        self.app.tabs.setEnabled(False)

    def create_daily_management_tab(self):
        """إنشاء تبويب إدارة اليوم مع تنظيم واضح"""
        layout = QVBoxLayout(self.app.tab_daily_management)
        layout.addWidget(self.app.date_warning_label)
        layout.setSpacing(15)  # مسافة بين المجموعات

        # ═══════════════════════════════════════════════════════
        # قسم 1: يوم العمل (التاريخ والفترة)
        # ═══════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════
        # قسم 1: يوم العمل (التاريخ والفترة)
        # ═══════════════════════════════════════════════════════
        active_date_group = QGroupBox("📅 يوم العمل")
        active_date_group.setStyleSheet("QGroupBox { margin-top: 10px; padding-top: 10px; font-weight: bold; }")
        active_date_layout = QGridLayout(active_date_group)
        active_date_layout.setSpacing(10)
        active_date_layout.setContentsMargins(15, 20, 15, 15)
    
        # عناصر التاريخ
        self.app.main_date_edit = QDateEdit(QDate.currentDate())
        self.app.main_date_edit.setCalendarPopup(True)
        self.app.main_date_edit.setDisplayFormat("yyyy-MM-dd (dddd)")
        self.app.main_date_edit.dateChanged.connect(self.app._on_main_date_changed)
    
        btn_goto_today = QPushButton(" العودة لليوم")
        btn_goto_today.setIcon(qta.icon('fa5s.calendar-day'))
        btn_goto_today.clicked.connect(lambda: self.app.main_date_edit.setDate(QDate.currentDate()))
    
        # عناصر الفترة
        self.app.time_slot_combo = QComboBox()
        self.app.time_slot_combo.currentTextChanged.connect(self.app._on_time_slot_changed)
    
        # إنشاء عناوين بحجم خط مناسب
        label_date = QLabel("<b>التاريخ:</b>")
        label_period = QLabel("<b>الفترة (الحصة):</b>")
        
        for label in [label_date, label_period]:
            label.setFont(QFont("Amiri", 13, QFont.Bold))
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # ترتيب العناصر في الشبكة
        active_date_layout.addWidget(label_date, 0, 0)
        active_date_layout.addWidget(self.app.main_date_edit, 0, 1)
        active_date_layout.addWidget(btn_goto_today, 0, 2)
        active_date_layout.addWidget(label_period, 1, 0)
        active_date_layout.addWidget(self.app.time_slot_combo, 1, 1, 1, 2)
        
        # تحديد نسب الأعمدة
        active_date_layout.setColumnStretch(0, 0)  # عمود العناوين
        active_date_layout.setColumnStretch(1, 2)  # عمود الحقول
        active_date_layout.setColumnStretch(2, 1)  # عمود الزر

        # ═══════════════════════════════════════════════════════
        # قسم 2: تفاصيل الدرس
        # ═══════════════════════════════════════════════════════
        # ═══════════════════════════════════════════════════════
        # قسم 2: تفاصيل الدرس
        # ═══════════════════════════════════════════════════════
        lesson_group = QGroupBox("📚 تفاصيل الدرس للربط بالتقويم")
        lesson_group.setStyleSheet("QGroupBox { margin-top: 20px; padding-top: 10px; font-weight: bold; }")
        lesson_layout = QVBoxLayout(lesson_group)
        lesson_layout.setSpacing(12)
        lesson_layout.setContentsMargins(15, 25, 15, 15)
    
        # لافتة التنبيه للدروس المحفوظة
        self.app.saved_lessons_alert = QLabel()
        self.app.saved_lessons_alert.setStyleSheet(
            "background-color: #fff3cd; color: #856404; padding: 10px; "
            "border: 1px solid #ffeaa7; border-radius: 5px; font-weight: bold;"
        )
        self.app.saved_lessons_alert.setAlignment(Qt.AlignCenter)
        self.app.saved_lessons_alert.setVisible(False)
        self.app.saved_lessons_alert.setWordWrap(True)
        lesson_layout.addWidget(self.app.saved_lessons_alert)
    
        # نموذج تفاصيل الدرس
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)
        
        # حقول الإدخال
        self.app.lesson_unit_edit = QLineEdit()
        self.app.lesson_domain_edit = QLineEdit()
        self.app.lesson_content_edit = QLineEdit()
        self.app.lesson_unit_edit.setPlaceholderText("مثال: المقطع الأول")
        self.app.lesson_domain_edit.setPlaceholderText("مثال: فهم المنطوق")
        self.app.lesson_content_edit.setPlaceholderText("مثال: نص 'في ساحة المدرسة'")
    
        # العناوين
        label_unit = QLabel("<b>المقطع:</b>")
        label_domain = QLabel("<b>الميدان:</b>")
        label_content = QLabel("<b>المحتوى:</b>")
        
        for label in [label_unit, label_domain, label_content]:
            label.setFont(QFont("Amiri", 13, QFont.Bold))
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setMinimumWidth(100)  # توحيد عرض العناوين
            label.setMaximumWidth(120)  # حد أقصى للعرض
        
        # ترتيب النموذج
        form_layout.addWidget(label_unit, 0, 0)
        form_layout.addWidget(self.app.lesson_unit_edit, 0, 1)
        form_layout.addWidget(label_domain, 1, 0)
        form_layout.addWidget(self.app.lesson_domain_edit, 1, 1)
        form_layout.addWidget(label_content, 2, 0)
        form_layout.addWidget(self.app.lesson_content_edit, 2, 1)
        
        form_layout.setColumnStretch(0, 0)  # عمود العناوين - عرض ثابت
        form_layout.setColumnStretch(1, 1)  # عمود الحقول - يتمدد
        
        lesson_layout.addLayout(form_layout)
    
        # أزرار الإجراءات
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
    
        btn_start_lesson = self.app._create_button(
            " بدء / تحديث الدرس", 
            icon='fa5s.play-circle', 
            callback=self.app._start_or_update_lesson,
            style="background-color: #27ae60;"
        )
    
        btn_review_lessons = self.app._create_button(
            " استعراض الدروس المحفوظة", 
            icon='fa5s.history', 
            callback=self.app.open_previous_lessons_dialog,
            style="background-color: #3498db;"
        )
    
        buttons_layout.addWidget(btn_start_lesson)
        buttons_layout.addWidget(btn_review_lessons)
        buttons_layout.addStretch()
        
        lesson_layout.addLayout(buttons_layout)
    
        # ملاحظة الحالة الحالية
        self.app.current_lesson_label = QLabel("أدخل تفاصيل الدرس واضغط 'بدء' لربط التقييمات به.")
        self.app.current_lesson_label.setStyleSheet("font-style: italic; color: #7f8c8d; padding: 5px;")
        self.app.current_lesson_label.setWordWrap(True)
        lesson_layout.addWidget(self.app.current_lesson_label)

        # ═══════════════════════════════════════════════════════
        # إضافة المجموعات إلى التخطيط الرئيسي
        # ═══════════════════════════════════════════════════════
        layout.addWidget(active_date_group)
        layout.addWidget(lesson_group)
        layout.addStretch()

    def create_timeline_tab(self):
        main_layout = QVBoxLayout(self.app.tab_timeline)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>السجل الزمني المتكامل لجميع أنشطة التلميذ</b>"))
        header_layout.addStretch()
        btn_comm = QPushButton(" 📞 تواصل مع ولي الأمر")
        btn_comm.setStyleSheet("background-color: #8e44ad;")
        btn_comm.clicked.connect(self.app._open_communication_dialog)
        header_layout.addWidget(btn_comm)
        
        self.app.timeline_display = QTextBrowser()
        self.app.timeline_display.setOpenExternalLinks(True)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.app.timeline_display, 1)

    def create_attendance_tab(self):
        main_layout = QVBoxLayout(self.app.tab_attendance)
        header_layout = QHBoxLayout()
        self.app.attendance_date_label = QLabel("<b>سجل الحضور لليوم الحالي</b>")
        header_layout.addWidget(self.app.attendance_date_label)
        header_layout.addStretch()
        
        btn_report = self.app._create_button(text=" 📊 مركز المراقبة", callback=self.app._open_attendance_center, style="background-color: #9b59b6;")
        header_layout.addWidget(btn_report)
        header_layout.addSpacing(15)

        btn_all_present = QPushButton("حضور الجميع")
        btn_all_present.setIcon(qta.icon('fa5s.users'))
        btn_all_present.setStyleSheet("background-color: #16a085;")
        btn_all_present.clicked.connect(lambda: self.app._set_all_attendance("حاضر"))
        header_layout.addWidget(btn_all_present)
        main_layout.addLayout(header_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.app.attendance_grid = QGridLayout(scroll_content)
        self.app.attendance_grid.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)

    def create_behavior_tab(self):
        main_layout = QVBoxLayout(self.app.tab_behavior)
        main_layout.setAlignment(Qt.AlignTop)
        
        quick_actions_group = QGroupBox("تسجيل سلوك سريع (للتلميذ المحدد)")
        quick_actions_layout = QVBoxLayout(quick_actions_group)
        
        positive_layout = QHBoxLayout()
        positive_layout.addWidget(QLabel("<b>إيجابي:</b>"))
        btn_pos_1 = QPushButton("👍 مشاركة (+5)")
        btn_pos_1.setStyleSheet("background-color: #27ae60;")
        btn_pos_1.clicked.connect(lambda: self.app._record_behavior(5, "مشاركة ممتازة"))
        btn_pos_2 = QPushButton("🤝 مساعدة (+3)")
        btn_pos_2.setStyleSheet("background-color: #27ae60;")
        btn_pos_2.clicked.connect(lambda: self.app._record_behavior(3, "مساعدة زميل"))
        positive_layout.addWidget(btn_pos_1)
        positive_layout.addWidget(btn_pos_2)
        positive_layout.addStretch()
        
        negative_layout = QHBoxLayout()
        negative_layout.addWidget(QLabel("<b>سلبي:</b>"))
        btn_neg_1 = QPushButton("🗣️ إزعاج (-2)")
        btn_neg_1.setStyleSheet("background-color: #c0392b;")
        btn_neg_1.clicked.connect(lambda: self.app._record_behavior(-2, "إزعاج/كلام في الفصل"))
        btn_neg_2 = QPushButton("✏️ بدون أدوات (-1)")
        btn_neg_2.setStyleSheet("background-color: #c0392b;")
        btn_neg_2.clicked.connect(lambda: self.app._record_behavior(-1, "لم يحضر أدواته"))
        negative_layout.addWidget(btn_neg_1)
        negative_layout.addWidget(btn_neg_2)
        negative_layout.addStretch()
        
        quick_actions_layout.addLayout(positive_layout)
        quick_actions_layout.addLayout(negative_layout)
        
        custom_entry_group = QGroupBox("تسجيل سلوك مخصص")
        custom_layout = QHBoxLayout(custom_entry_group)
        self.app.behavior_points_spin = QSpinBox()
        self.app.behavior_points_spin.setRange(-20, 20)
        self.app.behavior_note_edit = QLineEdit()
        self.app.behavior_note_edit.setPlaceholderText("اكتب ملاحظة السلوك هنا...")
        btn_save_custom = QPushButton("حفظ")
        btn_save_custom.setIcon(qta.icon('fa5s.save'))
        btn_save_custom.clicked.connect(self.app._record_custom_behavior)
        custom_layout.addWidget(QLabel("النقاط:"))
        custom_layout.addWidget(self.app.behavior_points_spin)
        custom_layout.addWidget(QLabel("الملاحظة:"))
        custom_layout.addWidget(self.app.behavior_note_edit, 1)
        custom_layout.addWidget(btn_save_custom)

        log_group = QGroupBox("سجل السلوك لليوم الحالي")
        log_layout = QVBoxLayout(log_group)
        self.app.behavior_log_display = QTextBrowser()
        log_layout.addWidget(self.app.behavior_log_display)

        main_layout.addWidget(quick_actions_group)
        main_layout.addWidget(custom_entry_group)
        main_layout.addWidget(log_group, 1)

    def create_academic_tab(self):
        main_layout = QVBoxLayout(self.app.tab_academic)
        controls_layout = QHBoxLayout()
        self.app.academic_subject_combo = QComboBox()
        self.app.academic_subject_combo.addItems(self.app.academic_subjects)
        
        self.app.academic_group_selector = QComboBox()
        self.app.academic_group_selector.currentIndexChanged.connect(self.app._filter_academic_grid_by_group)

        controls_layout.addWidget(QLabel("<b>المادة:</b>"))
        controls_layout.addWidget(self.app.academic_subject_combo)
        controls_layout.addWidget(QLabel("<b>المجموعة:</b>"))
        controls_layout.addWidget(self.app.academic_group_selector)
        controls_layout.addStretch()

        btn_apply_all_academic = self.app._create_button(text="📋 تطبيق على الكل", callback=self.app._apply_quick_academic_evaluation, style="background-color: #16a085;")
        controls_layout.addWidget(btn_apply_all_academic)
        
        self.app.academic_subject_combo.currentTextChanged.connect(self.app.update_academic_evaluation_grid_values)
        main_layout.addLayout(controls_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.app.academic_grid = QGridLayout(scroll_content)
        self.app.academic_grid.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        btn_save = self.app._create_button(text="حفظ التقييمات الأكاديمية", icon='fa5s.save', callback=self.app.save_academic_evaluations, obj_name="actionButton")
        main_layout.addWidget(btn_save, alignment=Qt.AlignRight)

    def create_evaluation_tab(self):
        main_layout = QVBoxLayout(self.app.tab_evaluation)
        header_layout = QHBoxLayout()
        self.app.eval_group_selector = QComboBox()
        self.app.eval_group_selector.currentIndexChanged.connect(self.app._filter_eval_list_by_group)
        
        header_layout.addWidget(QLabel("<b>فلترة حسب:</b>"))
        header_layout.addWidget(self.app.eval_group_selector)
        header_layout.addStretch()
        
        btn_apply_all = self.app._create_button(text="📋 تطبيق على الكل", callback=self.app._apply_quick_evaluation, style="background-color: #16a085;")
        header_layout.addWidget(btn_apply_all)
        
        btn_select_sample = self.app._create_button(text="🎯 عينة", callback=self.app._select_evaluation_sample, style="background-color: #e67e22;")
        btn_edit_criteria = self.app._create_button(icon='fa5s.cog', tip="تعديل معايير التقويم", callback=self.app.edit_evaluation_criteria, obj_name="toolButton")
        header_layout.addWidget(btn_select_sample)
        header_layout.addWidget(btn_edit_criteria)
        
        body_splitter = QSplitter(Qt.Horizontal)
        
        students_frame = QFrame()
        students_layout = QVBoxLayout(students_frame)
        self.app.eval_student_list = QListWidget()
        self.app.eval_student_list.currentItemChanged.connect(self.app._display_student_evaluation_form)
        students_layout.addWidget(self.app.eval_student_list)
        
        self.app.eval_form_frame = QFrame()
        self.app.eval_form_layout = QFormLayout(self.app.eval_form_frame)
        self.app.eval_form_layout.setContentsMargins(15, 15, 15, 15)
        self.app.eval_form_layout.setSpacing(15)
        
        body_splitter.addWidget(self.app.eval_form_frame)
        body_splitter.addWidget(students_frame)
        body_splitter.setSizes([400, 200])

        btn_save = self.app._create_button(text="حفظ كل التقييمات للدرس الحالي", icon='fa5s.save', callback=self.app.save_daily_evaluations, obj_name="actionButton")
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(body_splitter, 1)
        main_layout.addWidget(btn_save, 0, Qt.AlignRight)

    def create_grades_tab(self):
        layout = QHBoxLayout(self.app.tab_grades)
        
        charts_group = QGroupBox("ملخص الأداء المرئي")
        charts_layout = QVBoxLayout(charts_group)
        if self.app.CHARTS_ENABLED:
            charts_layout.addWidget(self.app.charts_canvas)
        else:
            charts_layout.addWidget(QLabel("مكتبة الرسوم البيانية 'Matplotlib' غير مثبتة.\n<pre>pip install matplotlib</pre>"))
        
        text_analysis_group = QGroupBox("تحليل وأدوات")
        text_layout = QVBoxLayout(text_analysis_group)
        self.app.report_display = QTextBrowser()
        self.app.report_display.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        buttons_layout = QHBoxLayout()
        self.app.btn_ai = self.app._create_button(" تحليل AI", icon='fa5s.robot', callback=self.app.run_ai_analysis, style="background-color: #8e44ad;")
        self.app.btn_ai.setEnabled(False)
        btn_pdf = self.app._create_button(" تصدير PDF", icon='fa5s.file-pdf', callback=self.app.export_student_pdf)
        if not self.app.PDF_ENABLED: btn_pdf.setEnabled(False)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.app.btn_ai)
        buttons_layout.addWidget(btn_pdf)
        
        text_layout.addWidget(self.app.report_display)
        text_layout.addLayout(buttons_layout)

        layout.addWidget(charts_group, 2)
        layout.addWidget(text_analysis_group, 1)

    def create_tools_tab(self):
        layout = QGridLayout(self.app.tab_tools)
        layout.setAlignment(Qt.AlignTop)
        
        btn_ask_expert = self.app._create_tool_button("اسأل الخبير التربوي", 'fa5s.brain', '#f39c12', self.app.open_ask_expert)
        if not self.app.AI_ENABLED: btn_ask_expert.setEnabled(False)
        
        btn_group_maker = self.app._create_tool_button("مُكوّن المجموعات", 'fa5s.users', '#1abc9c', self.app.open_group_maker)
        btn_daily_log = self.app._create_tool_button("السجل اليومي للقسم", 'fa5s.book', '#3498db', self.app.open_daily_log)
        btn_final_report = self.app._create_tool_button("إصدار كشف النقاط", 'fa5s.file-invoice', '#9b59b6', self.app.open_final_report_dialog)
        btn_review_lessons = self.app._create_tool_button("استعراض الدروس", 'fa5s.history', '#e67e22', self.app.open_previous_lessons_dialog)
        
        layout.addWidget(btn_ask_expert, 0, 0)
        layout.addWidget(btn_group_maker, 1, 0)
        layout.addWidget(btn_daily_log, 2, 0)
        layout.addWidget(btn_final_report, 0, 1)
        layout.addWidget(btn_review_lessons, 1, 1)

    def create_resources_tab(self):
        layout = QVBoxLayout(self.app.tab_resources)
        if not self.app.PDF_READER_ENABLED:
            label = QLabel("ميزة عرض ملفات PDF غير مفعلة.\nيرجى تثبيت مكتبة PyMuPDF باستخدام الأمر:\n<pre>pip install PyMuPDF</pre>")
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(label)
            return
            
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False) 
        
        self.app.pdf_viewer_label = DraggableLabel(scroll_area) 
        self.app.pdf_viewer_label.setAlignment(Qt.AlignCenter)
        self.app.pdf_viewer_label.setMinimumSize(400, 400)

        scroll_area.setWidget(self.app.pdf_viewer_label)
        
        controls_layout = QHBoxLayout()
        btn_open_pdf = QPushButton(" فتح ملف")
        btn_open_pdf.setIcon(qta.icon('fa5s.file-pdf'))
        btn_open_pdf.clicked.connect(self.app.open_pdf_file)
        
        self.app.pdf_prev_button = QPushButton("السابقة")
        self.app.pdf_prev_button.clicked.connect(self.app.show_previous_pdf_page)
        self.app.pdf_next_button = QPushButton("التالية")
        self.app.pdf_next_button.clicked.connect(self.app.show_next_pdf_page)
        self.app.pdf_page_label = QLabel("0 / 0")
        
        btn_zoom_out = QPushButton("")
        btn_zoom_out.setIcon(qta.icon('fa5s.search-minus'))
        btn_zoom_out.setToolTip("تصغير")
        btn_zoom_out.clicked.connect(self.app.zoom_out_pdf)

        btn_zoom_in = QPushButton("")
        btn_zoom_in.setIcon(qta.icon('fa5s.search-plus'))
        btn_zoom_in.setToolTip("تكبير")
        btn_zoom_in.clicked.connect(self.app.zoom_in_pdf)

        btn_toggle_pages = QPushButton("📖 عرض صفحتين")
        btn_toggle_pages.setCheckable(True)
        btn_toggle_pages.toggled.connect(self.app.toggle_two_page_mode)
        controls_layout.addWidget(btn_toggle_pages)
        
        self.app.zoom_slider = QSlider(Qt.Horizontal)
        self.app.zoom_slider.setMinimum(50)
        self.app.zoom_slider.setMaximum(400)
        self.app.zoom_slider.setValue(self.app.pdf_zoom_level)
        self.app.zoom_slider.setFixedWidth(120)
        self.app.zoom_slider.valueChanged.connect(self.app.set_pdf_zoom)
        self.app.zoom_label = QLabel(f"{int(self.app.pdf_zoom_level / 1.5)}%")
        
        controls_layout.addWidget(btn_open_pdf)
        controls_layout.addStretch()
        controls_layout.addWidget(self.app.pdf_prev_button)
        controls_layout.addWidget(self.app.pdf_page_label)
        controls_layout.addWidget(self.app.pdf_next_button)
        controls_layout.addStretch()
        controls_layout.addWidget(btn_zoom_out)
        controls_layout.addWidget(self.app.zoom_slider)
        controls_layout.addWidget(btn_zoom_in)
        controls_layout.addWidget(self.app.zoom_label)
        
        self.app.pdf_doc = None
        self.app.current_pdf_page = 0
        layout.addLayout(controls_layout)
        layout.addWidget(scroll_area, 1)

    def create_interactive_timetable_tab(self):
        self.app.tab_timetable_layout = QVBoxLayout(self.app.tab_timetable)

        info_layout = QHBoxLayout()
        info_label = QLabel("يعرض هذا الجدول التوقيت الذي تم إعداده من قائمة 'ملف'. الخانة الملونة تمثل الحصة الحالية.")
        info_label.setWordWrap(True)
    
        info_icon_label = QLabel()
        icon_pixmap = qta.icon('fa5s.info-circle', color='#3498db').pixmap(QSize(16, 16))
        info_icon_label.setPixmap(icon_pixmap)
        info_layout.addWidget(info_icon_label)
        info_layout.addWidget(info_label, 1)
    
        self.app.timetable_table = QTableWidget()
        self.app.timetable_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.app.tab_timetable_layout.addLayout(info_layout)
        self.app.tab_timetable_layout.addWidget(self.app.timetable_table)

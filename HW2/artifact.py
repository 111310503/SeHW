"""
國立金門大學 (NQU) 簡易校務系統示範專案
National Quemoy University Academic Information System Simulation

功能特點：
1. 學生模組：查詢個人資料、選課、退選、查詢學期成績單與 GPA。
2. 教師模組：查詢授課清單、登錄/修改學生成績。
3. 管理員模組：使用者管理、課程開立與管理、全校學籍檢視。
4. 資料持久化：自動將資料儲存至 local JSON 檔案。
"""

import json
import os
import sys

DATA_FILE = "nqu_system_data.json"


class Course:
    def __init__(self, course_id, name, credits, instructor_id, capacity=30, enrolled_students=None):
        self.course_id = course_id
        self.name = name
        self.credits = credits
        self.instructor_id = instructor_id
        self.capacity = capacity
        self.enrolled_students = enrolled_students if enrolled_students is not None else []

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "name": self.name,
            "credits": self.credits,
            "instructor_id": self.instructor_id,
            "capacity": self.capacity,
            "enrolled_students": self.enrolled_students
        }


class User:
    def __init__(self, user_id, password, name, role):
        self.user_id = user_id
        self.password = password
        self.name = name
        self.role = role  # "student", "teacher", "admin"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "password": self.password,
            "name": self.name,
            "role": self.role
        }


class Student(User):
    def __init__(self, user_id, password, name, department, year, enrolled_courses=None, grades=None):
        super().__init__(user_id, password, name, role="student")
        self.department = department
        self.year = year
        self.enrolled_courses = enrolled_courses if enrolled_courses is not None else []
        # grades 格式: {course_id: score}
        self.grades = grades if grades is not None else {}

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "department": self.department,
            "year": self.year,
            "enrolled_courses": self.enrolled_courses,
            "grades": self.grades
        })
        return base

    def calculate_gpa(self, courses_dict):
        """依台灣大專院校常見 4.3 制 GPA 計算換算"""
        if not self.grades:
            return 0.0, 0

        total_points = 0.0
        total_credits = 0

        for cid, score in self.grades.items():
            if cid in courses_dict:
                cred = courses_dict[cid].credits
                total_credits += cred
                
                # 換算點數
                if score >= 90:
                    pts = 4.3
                elif score >= 85:
                    pts = 4.0
                elif score >= 80:
                    pts = 3.7
                elif score >= 77:
                    pts = 3.3
                elif score >= 73:
                    pts = 3.0
                elif score >= 70:
                    pts = 2.7
                elif score >= 67:
                    pts = 2.3
                elif score >= 63:
                    pts = 2.0
                elif score >= 60:
                    pts = 1.7
                else:
                    pts = 0.0
                
                total_points += (pts * cred)

        gpa = (total_points / total_credits) if total_credits > 0 else 0.0
        return round(gpa, 2), total_credits


class Teacher(User):
    def __init__(self, user_id, password, name, department):
        super().__init__(user_id, password, name, role="teacher")
        self.department = department

    def to_dict(self):
        base = super().to_dict()
        base.update({"department": self.department})
        return base


class Admin(User):
    def __init__(self, user_id, password, name):
        super().__init__(user_id, password, name, role="admin")


class NQUPortalSystem:
    def __init__(self):
        self.users = {}
        self.courses = {}
        self.current_user = None
        self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.init_default_data()
            self.save_data()
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 載入課程
            for c_data in data.get("courses", []):
                course = Course(
                    course_id=c_data["course_id"],
                    name=c_data["name"],
                    credits=c_data["credits"],
                    instructor_id=c_data["instructor_id"],
                    capacity=c_data["capacity"],
                    enrolled_students=c_data["enrolled_students"]
                )
                self.courses[course.course_id] = course

            # 載入使用者
            for u_data in data.get("users", []):
                role = u_data.get("role")
                if role == "student":
                    user = Student(
                        user_id=u_data["user_id"],
                        password=u_data["password"],
                        name=u_data["name"],
                        department=u_data["department"],
                        year=u_data["year"],
                        enrolled_courses=u_data.get("enrolled_courses", []),
                        grades=u_data.get("grades", {})
                    )
                elif role == "teacher":
                    user = Teacher(
                        user_id=u_data["user_id"],
                        password=u_data["password"],
                        name=u_data["name"],
                        department=u_data["department"]
                    )
                else:
                    user = Admin(
                        user_id=u_data["user_id"],
                        password=u_data["password"],
                        name=u_data["name"]
                    )
                self.users[user.user_id] = user
        except Exception as e:
            print(f"[警告] 資料檔讀取失敗，載入預設資料: {e}")
            self.init_default_data()

    def init_default_data(self):
        # 預設管理員
        admin = Admin("admin", "admin123", "系統管理員")
        
        # 預設教師
        t1 = Teacher("T101", "teach123", "陳教授", "資訊工程學系")
        t2 = Teacher("T102", "teach123", "李教授", "企業管理學系")
        
        # 預設學生 (金門大學學號範例: 111105001)
        s1 = Student("111105001", "stu123", "王小明", "資訊工程學系", 3)
        s2 = Student("111105002", "stu123", "張小美", "資訊工程學系", 3)
        
        # 預設課程
        c1 = Course("CS201", "資料結構", 3, "T101", 40)
        c2 = Course("CS202", "演算法", 3, "T101", 35)
        c3 = Course("BA101", "管理學原理", 2, "T102", 50)
        
        self.users = {
            admin.user_id: admin,
            t1.user_id: t1,
            t2.user_id: t2,
            s1.user_id: s1,
            s2.user_id: s2
        }
        self.courses = {
            c1.course_id: c1,
            c2.course_id: c2,
            c3.course_id: c3
        }

    def save_data(self):
        data = {
            "users": [u.to_dict() for u in self.users.values()],
            "courses": [c.to_dict() for c in self.courses.values()]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def login(self):
        print("\n" + "=" * 50)
        print("    國立金門大學 (NQU) 校務整合資訊系統")
        print("=" * 50)
        uid = input("請輸入帳號 (學號/教工編號): ").strip()
        pwd = input("請輸入密碼: ").strip()

        user = self.users.get(uid)
        if user and user.password == pwd:
            self.current_user = user
            print(f"\n[登入成功] 歡迎進入系統，{user.name} ({user.role})")
            return True
        else:
            print("\n[錯誤] 帳號或密碼不正確！")
            return False

    def run(self):
        while True:
            if not self.current_user:
                print("\n1. 系統登入")
                print("2. 離開系統")
                choice = input("請選擇操作 (1-2): ").strip()
                if choice == "1":
                    self.login()
                elif choice == "2":
                    print("感謝使用金門大學校務資訊系統，再見！")
                    sys.exit(0)
                else:
                    print("無效選項，請重新輸入。")
            else:
                if self.current_user.role == "student":
                    self.student_menu()
                elif self.current_user.role == "teacher":
                    self.teacher_menu()
                elif self.current_user.role == "admin":
                    self.admin_menu()

    # ---------------- 學生專區 ---------------- #
    def student_menu(self):
        stu = self.current_user
        print(f"\n=== 金大學生系統專區 [{stu.name} / {stu.user_id}] ===")
        print("1. 查詢個人學籍資料")
        print("2. 查詢全校開課清單")
        print("3. 線上選課加選")
        print("4. 線上選課退選")
        print("5. 查詢個人課表")
        print("6. 查詢學業成績單與 GPA")
        print("0. 登出系統")
        choice = input("請選擇功能 (0-6): ").strip()

        if choice == "1":
            print(f"\n[學籍資料]")
            print(f"學號: {stu.user_id} | 姓名: {stu.name}")
            print(f"學系: {stu.department} | 年級: {stu.year} 年級")
        elif choice == "2":
            self.display_all_courses()
        elif choice == "3":
            self.student_add_course(stu)
        elif choice == "4":
            self.student_drop_course(stu)
        elif choice == "5":
            self.student_view_timetable(stu)
        elif choice == "6":
            self.student_view_grades(stu)
        elif choice == "0":
            self.current_user = None
            print("[資訊] 已安全登出系統。")
        else:
            print("無效選項，請重試。")

    def display_all_courses(self):
        print("\n" + "-" * 60)
        print(f"{'課程代號':<10}{'課程名稱':<18}{'學分':<6}{'授課教師':<10}{'名額狀況'}")
        print("-" * 60)
        for cid, c in self.courses.items():
            teacher_name = self.users[c.instructor_id].name if c.instructor_id in self.users else "未知"
            enrollment_status = f"{len(c.enrolled_students)}/{c.capacity}"
            print(f"{c.course_id:<10}{c.name:<18}{c.credits:<6}{teacher_name:<10}{enrollment_status}")
        print("-" * 60)

    def student_add_course(self, student):
        self.display_all_courses()
        cid = input("請輸入欲加選的課程代號: ").strip()
        if cid not in self.courses:
            print("[提示] 找不到該課程代號。")
            return

        course = self.courses[cid]
        if cid in student.enrolled_courses:
            print("[警告] 您已經修習此課程，無法重複加選！")
            return

        if len(course.enrolled_students) >= course.capacity:
            print("[警告] 選課名額已滿，加選失敗！")
            return

        # 執行加選
        student.enrolled_courses.append(cid)
        course.enrolled_students.append(student.user_id)
        self.save_data()
        print(f"[成功] 已成功加選：{course.name} ({cid})")

    def student_drop_course(self, student):
        if not student.enrolled_courses:
            print("[提示] 目前尚無任何修課紀錄。")
            return

        print("\n[已選修課程清單]")
        for cid in student.enrolled_courses:
            c = self.courses.get(cid)
            c_name = c.name if c else "未知課程"
            print(f"- {cid}: {c_name}")

        cid = input("請輸入欲退選的課程代號: ").strip()
        if cid in student.enrolled_courses:
            student.enrolled_courses.remove(cid)
            if cid in self.courses and student.user_id in self.courses[cid].enrolled_students:
                self.courses[cid].enrolled_students.remove(student.user_id)
            if cid in student.grades:
                del student.grades[cid]
            self.save_data()
            print(f"[成功] 課程 {cid} 已成功退選。")
        else:
            print("[錯誤] 您未修習此課程。")

    def student_view_timetable(self, student):
        print(f"\n[{student.name} 的已選修課表]")
        if not student.enrolled_courses:
            print("目前無修習任何課程。")
            return
        
        total_cred = 0
        for cid in student.enrolled_courses:
            c = self.courses.get(cid)
            if c:
                t_name = self.users[c.instructor_id].name if c.instructor_id in self.users else "未知"
                print(f"代碼: {c.course_id} | 課名: {c.name:<12} | 學分: {c.credits} | 授課老師: {t_name}")
                total_cred += c.credits
        print(f"總修習學分: {total_cred} 學分")

    def student_view_grades(self, student):
        print(f"\n[{student.name} 學期成績單]")
        if not student.enrolled_courses:
            print("目前無任何修課紀錄。")
            return

        for cid in student.enrolled_courses:
            c = self.courses.get(cid)
            cname = c.name if c else cid
            score = student.grades.get(cid, "尚未登錄")
            print(f"課程: {cname:<12} ({cid}) -> 成績: {score}")

        gpa, credits_earned = student.calculate_gpa(self.courses)
        print("-" * 35)
        print(f"已核算學分: {credits_earned} 學分 | 平均 GPA: {gpa} / 4.3")

    # ---------------- 教師專區 ---------------- #
    def teacher_menu(self):
        teacher = self.current_user
        print(f"\n=== 金大教師教務專區 [{teacher.name} 老師] ===")
        print("1. 查詢我所授課的課程")
        print("2. 查詢指定課程之選課名冊")
        print("3. 登錄/修改學生成績")
        print("0. 登出系統")
        choice = input("請選擇功能 (0-3): ").strip()

        if choice == "1":
            self.teacher_list_courses(teacher)
        elif choice == "2":
            self.teacher_view_class_list(teacher)
        elif choice == "3":
            self.teacher_grade_input(teacher)
        elif choice == "0":
            self.current_user = None
            print("[資訊] 已安全登出系統。")
        else:
            print("無效選項，請重試。")

    def teacher_list_courses(self, teacher):
        print(f"\n[{teacher.name} 老師 授課清單]")
        my_courses = [c for c in self.courses.values() if c.instructor_id == teacher.user_id]
        if not my_courses:
            print("目前尚無排定授課科目。")
            return
        for c in my_courses:
            print(f"課程代號: {c.course_id} | 課名: {c.name:<12} | 學分: {c.credits} | 修課人數: {len(c.enrolled_students)}/{c.capacity}")

    def teacher_view_class_list(self, teacher):
        cid = input("請輸入欲查看名冊的課程代號: ").strip()
        c = self.courses.get(cid)
        if not c or c.instructor_id != teacher.user_id:
            print("[錯誤] 找不到此課程或您不是該課程授課教師。")
            return

        print(f"\n[{c.name} ({c.course_id}) 學生名冊]")
        if not c.enrolled_students:
            print("目前無學生選修此課程。")
            return

        for sid in c.enrolled_students:
            stu = self.users.get(sid)
            s_name = stu.name if stu else "未知"
            s_dept = stu.department if stu else "未知系所"
            score = stu.grades.get(cid, "未登錄") if stu else "N/A"
            print(f"學號: {sid} | 姓名: {s_name:<6} | 系所: {s_dept:<12} | 目前成績: {score}")

    def teacher_grade_input(self, teacher):
        cid = input("請輸入欲評分的課程代號: ").strip()
        c = self.courses.get(cid)
        if not c or c.instructor_id != teacher.user_id:
            print("[錯誤] 找不到此課程或您不是該課程授課教師。")
            return

        sid = input("請輸入學號: ").strip()
        if sid not in c.enrolled_students:
            print("[錯誤] 該名學生未修習此門課程。")
            return

        score_input = input("請輸入學生成績 (0-100): ").strip()
        try:
            score = float(score_input)
            if not (0 <= score <= 100):
                print("[錯誤] 分數必須介於 0 到 100 之間。")
                return
            student = self.users[sid]
            student.grades[cid] = score
            self.save_data()
            print(f"[成功] 已登記學號 {sid} 之 {c.name} 成績為: {score}")
        except ValueError:
            print("[錯誤] 請輸入有效數值！")

    # ---------------- 管理員專區 ---------------- #
    def admin_menu(self):
        admin = self.current_user
        print(f"\n=== 金大教務處系統管理員 [{admin.name}] ===")
        print("1. 新增開課科目")
        print("2. 建立新學生帳號")
        print("3. 建立新教師帳號")
        print("4. 檢視全校開課及選課狀況")
        print("0. 登出系統")
        choice = input("請選擇功能 (0-4): ").strip()

        if choice == "1":
            self.admin_add_course()
        elif choice == "2":
            self.admin_add_student()
        elif choice == "3":
            self.admin_add_teacher()
        elif choice == "4":
            self.display_all_courses()
        elif choice == "0":
            self.current_user = None
            print("[資訊] 已安全登出系統。")
        else:
            print("無效選項，請重試。")

    def admin_add_course(self):
        print("\n[新增開課]")
        cid = input("課程代號 (例如 CS301): ").strip()
        if cid in self.courses:
            print("[錯誤] 該課程代號已存在！")
            return
        name = input("課程名稱: ").strip()
        try:
            credits = int(input("學分數 (1-4): ").strip())
            capacity = int(input("修課名額上限: ").strip())
        except ValueError:
            print("[錯誤] 學分與名額必須為整數。")
            return

        inst_id = input("授課教師編號: ").strip()
        if inst_id not in self.users or self.users[inst_id].role != "teacher":
            print("[警告] 教師代號不存在或該使用者非教師，仍先建立課程。")

        self.courses[cid] = Course(cid, name, credits, inst_id, capacity)
        self.save_data()
        print(f"[成功] 課程 {name} ({cid}) 建立完成。")

    def admin_add_student(self):
        print("\n[建立新學生帳籍]")
        uid = input("學號: ").strip()
        if uid in self.users:
            print("[錯誤] 此學號已存在！")
            return
        pwd = input("預設密碼: ").strip()
        name = input("姓名: ").strip()
        dept = input("就讀學系 (例如: 資訊工程學系): ").strip()
        try:
            year = int(input("年級 (1-4): ").strip())
        except ValueError:
            year = 1

        self.users[uid] = Student(uid, pwd, name, dept, year)
        self.save_data()
        print(f"[成功] 學生 {name} ({uid}) 帳號已建立。")

    def admin_add_teacher(self):
        print("\n[建立新教師帳號]")
        uid = input("教師編號: ").strip()
        if uid in self.users:
            print("[錯誤] 此編號已存在！")
            return
        pwd = input("預設密碼: ").strip()
        name = input("姓名: ").strip()
        dept = input("所屬學系: ").strip()

        self.users[uid] = Teacher(uid, pwd, name, dept)
        self.save_data()
        print(f"[成功] 教師 {name} ({uid}) 帳號已建立。")


if __name__ == "__main__":
    system = NQUPortalSystem()
    system.run()